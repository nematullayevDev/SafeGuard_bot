from datetime import datetime, timedelta
from app.repositories.base import BaseRepository, get_conn

class SubscriptionRepository(BaseRepository):
    # ---- User subscriptions ----
    def get_user_plan(self, user_id: int) -> dict:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT plan, expires_at FROM user_subscriptions WHERE user_id = ?", (user_id,)
            ).fetchone()
        if not row:
            return {"plan": "free", "expires_at": None}
        plan, expires_at = row
        if plan == "premium" and expires_at:
            try:
                expires_dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return {"plan": "free", "expires_at": None}
            if datetime.now() > expires_dt:
                # Expired -> Revert to free
                self.deactivate_user_premium(user_id)
                return {"plan": "free", "expires_at": None}
        return {"plan": plan, "expires_at": expires_at}

    def activate_user_premium(self, user_id: int, days: int) -> None:
        expires = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO user_subscriptions (user_id, plan, expires_at, warning_sent) "
                "VALUES (?, 'premium', ?, 0) "
                "ON CONFLICT(user_id) DO UPDATE SET plan='premium', expires_at=?, warning_sent=0",
                (user_id, expires, expires),
            )

    def deactivate_user_premium(self, user_id: int) -> None:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO user_subscriptions (user_id, plan, expires_at, warning_sent) "
                "VALUES (?, 'free', NULL, 0) "
                "ON CONFLICT(user_id) DO UPDATE SET plan='free', expires_at=NULL, warning_sent=0",
                (user_id,),
            )

    # ---- Group subscriptions ----
    def get_group_plan(self, chat_id: int) -> dict:
        # First check if the group's creator/adder has active Premium
        with get_conn() as conn:
            row = conn.execute("SELECT added_by FROM groups WHERE chat_id = ?", (chat_id,)).fetchone()
        if row and row[0]:
            added_by = row[0]
            user_plan = self.get_user_plan(added_by)
            if user_plan["plan"] == "premium":
                return user_plan

        # Revert to direct group subscription if creator is not premium
        with get_conn() as conn:
            row = conn.execute(
                "SELECT plan, expires_at FROM group_subscriptions WHERE chat_id = ?", (chat_id,)
            ).fetchone()
        if not row:
            return {"plan": "free", "expires_at": None}
        plan, expires_at = row
        if plan == "premium" and expires_at:
            try:
                expires_dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return {"plan": "free", "expires_at": None}
            if datetime.now() > expires_dt:
                self.deactivate_group_premium(chat_id)
                return {"plan": "free", "expires_at": None}
        return {"plan": plan, "expires_at": expires_at}

    def activate_group_premium(self, chat_id: int, days: int) -> None:
        expires = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO group_subscriptions (chat_id, plan, expires_at, warning_sent) "
                "VALUES (?, 'premium', ?, 0) "
                "ON CONFLICT(chat_id) DO UPDATE SET plan='premium', expires_at=?, warning_sent=0",
                (chat_id, expires, expires),
            )

    def deactivate_group_premium(self, chat_id: int) -> None:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO group_subscriptions (chat_id, plan, expires_at, warning_sent) "
                "VALUES (?, 'free', NULL, 0) "
                "ON CONFLICT(chat_id) DO UPDATE SET plan='free', expires_at=NULL, warning_sent=0",
                (chat_id,),
            )

    # ---- AI quota usage ----
    def get_ai_usage_today(self, chat_id: int) -> int:
        today = datetime.now().strftime("%Y-%m-%d")
        with get_conn() as conn:
            row = conn.execute(
                "SELECT call_count FROM ai_quota_usage WHERE chat_id = ? AND usage_date = ?",
                (chat_id, today)
            ).fetchone()
        return row[0] if row else 0

    def increment_ai_usage(self, chat_id: int) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO ai_quota_usage (chat_id, usage_date, call_count) VALUES (?, ?, 1) "
                "ON CONFLICT(chat_id, usage_date) DO UPDATE SET call_count = call_count + 1",
                (chat_id, today),
            )
