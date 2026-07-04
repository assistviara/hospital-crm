from datetime import timedelta

from django.utils import timezone

from apps.referrals.models import ReferralRecord
from apps.visits.models import VisitRecord


class AnalyticsService:
    @staticmethod
    def _clamp_score(score):
        return max(0, min(100, round(score)))

    @staticmethod
    def calculate_home_return_score(hospital):
        score = 0
        total_beds = hospital.total_beds or 0

        score += min(hospital.community_beds or 0, 30)
        score += min(hospital.recovery_beds or 0, 30)
        score += min((hospital.general_beds or 0) / 5, 20)
        score += min((hospital.msw_count or 0) * 2, 10)
        score += min((hospital.discharge_nurse_count or 0) * 2, 10)

        if total_beds > 0:
            chronic_ratio = (hospital.chronic_beds or 0) / total_beds
            psychiatric_ratio = (hospital.psychiatric_beds or 0) / total_beds
            if chronic_ratio >= 0.5:
                score -= 20
            elif chronic_ratio >= 0.3:
                score -= 10
            if psychiatric_ratio >= 0.5:
                score -= 20
            elif psychiatric_ratio >= 0.3:
                score -= 10

        return AnalyticsService._clamp_score(score)

    @staticmethod
    def calculate_sales_potential_score(hospital):
        corporation = hospital.corporation
        if corporation is None:
            return 50

        score = 0
        if not corporation.has_care_management:
            score += 25
        if not corporation.has_home_nursing:
            score += 15
        if not corporation.has_geriatric_health_facility:
            score += 10

        internal_service_count = sum(
            [
                corporation.has_care_management,
                corporation.has_home_nursing,
                corporation.has_home_care,
                corporation.has_day_service,
                corporation.has_day_care,
                corporation.has_geriatric_health_facility,
                corporation.has_senior_housing,
                corporation.has_paid_nursing_home,
            ]
        )
        if internal_service_count >= 6:
            score -= 20
        elif internal_service_count >= 4:
            score -= 10

        return AnalyticsService._clamp_score(score)

    @staticmethod
    def calculate_activity_score(hospital):
        visits = VisitRecord.objects.filter(hospital=hospital)
        visit_count = visits.count()
        if visit_count == 0:
            return 0

        score = 20
        today = timezone.localdate()
        latest_visit = visits.order_by("-visit_date").first()

        if latest_visit and latest_visit.visit_date >= today - timedelta(days=90):
            score += 30
        elif latest_visit and latest_visit.visit_date < today - timedelta(days=180):
            score -= 20

        if visits.filter(follow_status__in=["todo", "doing"]).exists():
            score += 20
        if visits.exclude(positive_response="").exists():
            score += 20

        concern_count = visits.exclude(concern="").count()
        if concern_count >= 3:
            score -= 20
        elif concern_count >= 1:
            score -= 10

        return AnalyticsService._clamp_score(score)

    @staticmethod
    def calculate_referral_score(hospital):
        referrals = ReferralRecord.objects.filter(hospital=hospital)
        totals = {
            "case_count": sum(referral.case_count or 0 for referral in referrals),
            "contract_count": sum(referral.contract_count or 0 for referral in referrals),
        }
        case_count = totals["case_count"]
        contract_count = totals["contract_count"]
        if case_count == 0 and contract_count == 0:
            return 0

        score = 0
        if case_count > 0:
            score += min(case_count * 5, 40)
        if contract_count > 0:
            score += min(contract_count * 10, 30)
        if case_count > 0:
            contract_rate = contract_count / case_count
            if contract_rate >= 0.5:
                score += 30
            elif contract_rate >= 0.25:
                score += 20
            elif contract_rate > 0:
                score += 10

        return AnalyticsService._clamp_score(score)

    @staticmethod
    def calculate_priority_score(hospital):
        home_return_score = AnalyticsService.calculate_home_return_score(hospital)
        sales_potential_score = AnalyticsService.calculate_sales_potential_score(hospital)
        activity_score = AnalyticsService.calculate_activity_score(hospital)
        referral_score = AnalyticsService.calculate_referral_score(hospital)

        score = (
            home_return_score * 0.35
            + sales_potential_score * 0.30
            + activity_score * 0.20
            + referral_score * 0.15
        )
        return AnalyticsService._clamp_score(score)

    @staticmethod
    def get_rank(score):
        if score >= 90:
            return "S"
        if score >= 80:
            return "A"
        if score >= 70:
            return "B"
        if score >= 60:
            return "C"
        return "D"

    @staticmethod
    def get_score_reasons(hospital):
        reasons = []
        corporation = hospital.corporation
        visits = VisitRecord.objects.filter(hospital=hospital)
        referrals = ReferralRecord.objects.filter(hospital=hospital)

        if hospital.community_beds > 0:
            reasons.append("地域包括ケア病床があるため在宅復帰可能性が高い")
        if hospital.recovery_beds > 0:
            reasons.append("回復期リハ病床があるため在宅復帰支援との親和性がある")
        if hospital.msw_count > 0 or hospital.discharge_nurse_count > 0:
            reasons.append("MSWまたは退院支援看護師が配置されている")

        if corporation is None:
            reasons.append("法人が未設定のため営業余地を個別確認できる")
        else:
            if not corporation.has_care_management:
                reasons.append("法人内居宅介護支援がないため外部紹介余地がある")
            if not corporation.has_home_nursing:
                reasons.append("法人内訪問看護がないため退院後サービスの提案余地がある")
            if not corporation.has_geriatric_health_facility:
                reasons.append("法人内老健がないため外部連携余地がある")

        today = timezone.localdate()
        latest_visit = visits.order_by("-visit_date").first()
        if latest_visit and latest_visit.visit_date >= today - timedelta(days=90):
            reasons.append("直近90日以内に訪問済み")
        elif not latest_visit:
            reasons.append("訪問記録がないため新規接点づくりが必要")
        else:
            reasons.append("直近90日以内の訪問がないため再訪問余地がある")

        if visits.filter(follow_status__in=["todo", "doing"]).exists():
            reasons.append("フォロー未完了の訪問記録がある")
        if visits.exclude(positive_response="").exists():
            reasons.append("好反応がある")
        if referrals.exists() and any((referral.case_count or 0) > 0 for referral in referrals):
            reasons.append("紹介実績がある")
        if not reasons:
            reasons.append("分析に使える実績データがまだ少ない")

        return reasons

    @staticmethod
    def analyze_hospital(hospital):
        home_return_score = AnalyticsService.calculate_home_return_score(hospital)
        sales_potential_score = AnalyticsService.calculate_sales_potential_score(hospital)
        activity_score = AnalyticsService.calculate_activity_score(hospital)
        referral_score = AnalyticsService.calculate_referral_score(hospital)
        priority_score = AnalyticsService.calculate_priority_score(hospital)

        return {
            "home_return_score": home_return_score,
            "sales_potential_score": sales_potential_score,
            "activity_score": activity_score,
            "referral_score": referral_score,
            "priority_score": priority_score,
            "rank": AnalyticsService.get_rank(priority_score),
            "reasons": AnalyticsService.get_score_reasons(hospital),
        }
