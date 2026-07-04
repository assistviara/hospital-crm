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

        if hospital.community_beds > 0:
            score += 30
        if hospital.recovery_beds > 0:
            score += 30
        if hospital.general_beds > 0:
            score += 15
        if hospital.msw_count > 0:
            score += 10
        if hospital.discharge_nurse_count > 0:
            score += 10
        if hospital.has_regional_cooperation:
            score += 5

        if total_beds > 0:
            chronic_ratio = (hospital.chronic_beds or 0) / total_beds
            psychiatric_ratio = (hospital.psychiatric_beds or 0) / total_beds
            if chronic_ratio >= 0.7:
                score -= 20
            if psychiatric_ratio >= 0.7:
                score -= 20

        return AnalyticsService._clamp_score(score)

    @staticmethod
    def calculate_sales_potential_score(hospital):
        corporation = hospital.corporation
        if corporation is None:
            return 50

        score = 50

        if corporation.has_care_management:
            score -= 20
        else:
            score += 25

        if corporation.has_home_nursing:
            score -= 5
        else:
            score += 10

        if corporation.has_geriatric_health_facility:
            score -= 10
        else:
            score += 10

        if corporation.has_senior_housing or corporation.has_paid_nursing_home:
            score -= 5

        return AnalyticsService._clamp_score(score)

    @staticmethod
    def calculate_activity_score(hospital):
        visits = VisitRecord.objects.filter(hospital=hospital)
        if not visits.exists():
            return 70

        score = 0
        today = timezone.localdate()
        latest_visit = visits.order_by("-visit_date").first()
        days_since_visit = (today - latest_visit.visit_date).days

        if days_since_visit >= 180:
            score += 20
        elif days_since_visit >= 90:
            score += 10
        else:
            score += 5

        if visits.filter(follow_status__in=["todo", "doing"]).exists():
            score += 15
        if visits.exclude(positive_response="").exists():
            score += 10
        if visits.exclude(concern="").exists():
            score -= 10

        return AnalyticsService._clamp_score(score)

    @staticmethod
    def calculate_referral_score(hospital):
        referrals = ReferralRecord.objects.filter(hospital=hospital)
        if not referrals.exists():
            return 40

        case_count = sum(referral.case_count or 0 for referral in referrals)
        contract_count = sum(referral.contract_count or 0 for referral in referrals)

        score = 0
        if case_count >= 1:
            score += 30
        if contract_count >= 1:
            score += 20
        if case_count > 0 and contract_count / case_count >= 0.5:
            score += 10

        return AnalyticsService._clamp_score(score)

    @staticmethod
    def calculate_priority_score(hospital):
        home_return_score = AnalyticsService.calculate_home_return_score(hospital)
        sales_potential_score = AnalyticsService.calculate_sales_potential_score(hospital)
        activity_score = AnalyticsService.calculate_activity_score(hospital)
        referral_score = AnalyticsService.calculate_referral_score(hospital)

        score = (
            home_return_score * 0.40
            + sales_potential_score * 0.30
            + activity_score * 0.20
            + referral_score * 0.10
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
        total_beds = hospital.total_beds or 0
        visits = VisitRecord.objects.filter(hospital=hospital)
        referrals = ReferralRecord.objects.filter(hospital=hospital)

        if hospital.community_beds > 0:
            reasons.append("地域包括ケア病床があるため在宅復帰支援との接点が見込まれる")
        if hospital.recovery_beds > 0:
            reasons.append("回復期リハ病床があるため退院支援との接点が見込まれる")
        if total_beds > 0 and (hospital.chronic_beds or 0) / total_beds >= 0.7:
            reasons.append("療養病床割合が高いため在宅復帰は限定的な可能性がある")

        if corporation is None:
            reasons.append("法人情報が未設定のため営業余地を個別確認する必要がある")
        else:
            if corporation.has_care_management:
                reasons.append("法人内居宅介護支援があるため法人内完結の可能性がある")
            else:
                reasons.append("法人内居宅介護支援がないため外部居宅への紹介余地がある")

            if corporation.has_home_nursing:
                reasons.append("法人内訪問看護があるため訪問看護連携は法人内で完結する可能性がある")
            else:
                reasons.append("法人内訪問看護がないため退院後サービスの提案余地がある")

            if not corporation.has_geriatric_health_facility:
                reasons.append("法人内老健がないため外部連携余地がある")

        today = timezone.localdate()
        latest_visit = visits.order_by("-visit_date").first()
        if latest_visit is None:
            reasons.append("未訪問のため初回接点を作る余地がある")
        else:
            days_since_visit = (today - latest_visit.visit_date).days
            if days_since_visit >= 180:
                reasons.append("長期間未訪問のため再訪問候補")
            elif days_since_visit >= 90:
                reasons.append("90日以上訪問がないため再接点化の候補")

        if visits.filter(follow_status__in=["todo", "doing"]).exists():
            reasons.append("フォロー未対応の営業課題がある")
        if visits.exclude(positive_response="").exists():
            reasons.append("好反応の記録がある")

        case_count = sum(referral.case_count or 0 for referral in referrals)
        contract_count = sum(referral.contract_count or 0 for referral in referrals)
        if case_count > 0:
            reasons.append("紹介実績がある")
        else:
            reasons.append("まだ紹介実績がないため関係構築段階")
        if contract_count > 0:
            reasons.append("契約実績がある")

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
