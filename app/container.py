"""Minimal service container — wires repositories and services together."""
from dataclasses import dataclass

from app.core.bot import bot
from app.core.config import settings
from app.repositories import (
    BannedSiteRepository, BlacklistRepository, GroupRepository,
    HistoryRepository, SettingsRepository, StatsRepository,
    UserRepository, WarningRepository, ForensicRepository,
)
from app.services import (
    BroadcastService, ExportService, ModerationService,
    RateLimiter, ScanService, SpamDetector, VirusTotalService,
    UzbekNLPService, StateSyncService,
)


@dataclass(frozen=True)
class Container:
    # Repositories
    users: UserRepository
    blacklist: BlacklistRepository
    user_settings: SettingsRepository
    history: HistoryRepository
    warnings: WarningRepository
    groups: GroupRepository
    banned_sites: BannedSiteRepository
    stats: StatsRepository
    forensics: ForensicRepository

    # Services
    rate_limiter: RateLimiter
    spam: SpamDetector
    vt: VirusTotalService
    scanner: ScanService
    moderator: ModerationService
    broadcaster: BroadcastService
    exporter: ExportService
    nlp: UzbekNLPService
    state_sync: StateSyncService


def build_container() -> Container:
    users = UserRepository()
    blacklist = BlacklistRepository()
    user_settings = SettingsRepository()
    history = HistoryRepository()
    warnings = WarningRepository()
    groups = GroupRepository()
    banned_sites = BannedSiteRepository()
    stats = StatsRepository()
    forensics = ForensicRepository()

    rate_limiter = RateLimiter(settings.rate_limit_max, settings.rate_limit_window)
    spam = SpamDetector(settings.spam_keywords)
    vt = VirusTotalService(settings.vt_api_key)
    scanner = ScanService(vt, history, blacklist)
    moderator = ModerationService(bot, warnings, settings.max_warnings)
    broadcaster = BroadcastService(bot, users)
    exporter = ExportService()
    nlp = UzbekNLPService(settings.gemini_api_key)
    state_sync = StateSyncService(banned_sites, blacklist)

    return Container(
        users=users, blacklist=blacklist, user_settings=user_settings,
        history=history, warnings=warnings, groups=groups,
        banned_sites=banned_sites, stats=stats, forensics=forensics,
        rate_limiter=rate_limiter, spam=spam, vt=vt, scanner=scanner,
        moderator=moderator, broadcaster=broadcaster, exporter=exporter,
        nlp=nlp, state_sync=state_sync,
    )
