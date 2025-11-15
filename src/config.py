import os
import json
import logging
from dotenv import load_dotenv

# module logger
logger = logging.getLogger(__name__)

load_dotenv(override=True)

# Helper to load mappings from a separate JSON file. Path can be set via
# `MAPPINGS_FILE` env var, otherwise defaults to repo-root `mappings.json`.
def _load_from_mappings_file(key: str):
    mappings_path = os.getenv(
        "MAPPINGS_FILE",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mappings.json")),
    )
    if not os.path.exists(mappings_path):
        return None
    try:
        with open(mappings_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as e:
        logger.info(f"Failed to read mappings file '{mappings_path}': {e}")
        return None

    # mapping file expected to contain top-level keys: ROLES, RANK_EMOJI,
    # USER_NEWBEST_LIMIT, ROLE_THRESHOLDS
    return data.get(key)

# Discord configuration
if not (discord_token := os.getenv("DISCORD_TOKEN")):
    raise ValueError("DISCORD_TOKEN environment variable is required")
if not (server_id := os.getenv("SERVER_ID")):
    raise ValueError("SERVER_ID environment variable is required")
if not (channel_id := os.getenv("BOT_CHANNEL_ID")):
    raise ValueError("BOT_CHANNEL_ID environment variable is required")

DISCORD_TOKEN = discord_token
SERVER_ID = int(server_id)
BOT_CHANNEL_ID = int(channel_id)

# osu! API configuration
API_CLIENT_ID = os.getenv("API_CLIENT_ID")  # osu api client id
API_CLIENT_SECRET = os.getenv("API_CLIENT_SECRET")  # osu api client secret

# Database configuration
database_url = os.getenv("DATABASE_URL")
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_db = os.getenv("POSTGRES_DB")

DATABASE_URL = (
    database_url
    if database_url
    else f"postgresql://{postgres_user}:{postgres_password}@db:5432/{postgres_db}"
)

POST_REQUEST_URL = os.getenv("POST_REQUEST_URL")
POST_REQUEST_TOKEN = os.getenv("POST_REQUEST_TOKEN")

# Role ids for rank roles. Try `ROLES_JSON` env var first, then mappings file.
_roles_env = os.getenv("ROLES_JSON")
if not _roles_env:
    _roles_env = _load_from_mappings_file("ROLES")

if _roles_env:
    try:
        if isinstance(_roles_env, str):
            roles_obj = json.loads(_roles_env)
        else:
            roles_obj = _roles_env
        ROLES = {k: int(v) for k, v in roles_obj.items()}
    except Exception as e:
        raise ValueError(f"Invalid ROLES JSON provided (env or file): {e}")
else:
    logger.info("No role mappings configured (no ROLES_JSON env and no mappings file)")
    ROLES = {}

REV_ROLES = dict((v, k) for k, v in ROLES.items())
ROLES_VALUE = dict((key, count) for count, key in enumerate(ROLES.keys()))

# Single-value settings that can be provided via .env.
_pervert_role_env = os.getenv("PERVERT_ROLE")
if _pervert_role_env:
    try:
        PERVERT_ROLE = int(_pervert_role_env)
    except ValueError:
        raise ValueError("PERVERT_ROLE must be an integer role id")
else:
    # No pervert role configured in env
    logger.info("PERVERT_ROLE not configured; PERVERT_ROLE set to None")
    PERVERT_ROLE = None

# bot's discord id
_bot_self_env = os.getenv("BOT_SELF_ID")
if _bot_self_env:
    try:
        BOT_SELF_ID = int(_bot_self_env)
    except ValueError:
        raise ValueError("BOT_SELF_ID must be an integer id")
else:
    # No BOT_SELF_ID configured in env
    logger.info("BOT_SELF_ID not configured; BOT_SELF_ID set to None")
    BOT_SELF_ID = None

# channel id where new top scores and rank change messages will be sent
_botspam_env = os.getenv("BOTSPAM_CHANNEL_ID")
if _botspam_env:
    try:
        BOTSPAM_CHANNEL_ID = int(_botspam_env)
    except ValueError:
        raise ValueError("BOTSPAM_CHANNEL_ID must be an integer channel id")
else:
    # No BOTSPAM_CHANNEL_ID configured in env
    logger.info("BOTSPAM_CHANNEL_ID not configured; BOTSPAM_CHANNEL_ID set to None")
    BOTSPAM_CHANNEL_ID = None

# pp calculator needs int value but api returns mods as 2 characters
# Load MODS_DICT from env (MODS_DICT_JSON) or from mappings file; log if missing.
_mods_env = os.getenv("MODS_DICT_JSON")
if not _mods_env:
    _mods_env = _load_from_mappings_file("MODS_DICT")

if _mods_env:
    try:
        if isinstance(_mods_env, str):
            mods_obj = json.loads(_mods_env)
        else:
            mods_obj = _mods_env
        MODS_DICT = {k: int(v) for k, v in mods_obj.items()}
    except Exception as e:
        raise ValueError(f"Invalid MODS_DICT JSON provided (env or file): {e}")
else:
    logger.info("MODS_DICT not provided via env or mappings file; MODS_DICT set to empty mapping")
    MODS_DICT = {}

# emojis for rank achieved on top score post. Try env then mappings file.
_rank_emoji_env = os.getenv("RANK_EMOJI_JSON")
if not _rank_emoji_env:
    _rank_emoji_env = _load_from_mappings_file("RANK_EMOJI")

if _rank_emoji_env:
    try:
        if isinstance(_rank_emoji_env, str):
            RANK_EMOJI = json.loads(_rank_emoji_env)
        else:
            RANK_EMOJI = _rank_emoji_env
    except Exception as e:
        raise ValueError(f"Invalid RANK_EMOJI JSON provided (env or file): {e}")
else:
    logger.info("No rank emojis configured (no RANK_EMOJI_JSON env and no mappings file)")
    RANK_EMOJI = {}

# The personal top limit determining if a score should get posted
_user_newbest_env = os.getenv("USER_NEWBEST_LIMIT_JSON")
if not _user_newbest_env:
    _user_newbest_env = _load_from_mappings_file("USER_NEWBEST_LIMIT")

if _user_newbest_env:
    try:
        if isinstance(_user_newbest_env, str):
            ub_obj = json.loads(_user_newbest_env)
        else:
            ub_obj = _user_newbest_env
        USER_NEWBEST_LIMIT = {k: int(v) for k, v in ub_obj.items()}
    except Exception as e:
        raise ValueError(f"Invalid USER_NEWBEST_LIMIT JSON provided (env or file): {e}")
else:
    logger.info("No USER_NEWBEST_LIMIT configured (no env and no mappings file)")
    USER_NEWBEST_LIMIT = {}

# thresholds for rank roles. Try env then mappings file.
_role_thresholds_env = os.getenv("ROLE_THRESHOLDS_JSON")
if not _role_thresholds_env:
    _role_thresholds_env = _load_from_mappings_file("ROLE_THRESHOLDS")

if _role_thresholds_env:
    try:
        if isinstance(_role_thresholds_env, str):
            rt_obj = json.loads(_role_thresholds_env)
        else:
            rt_obj = _role_thresholds_env
        ROLE_TRESHOLDS = {k: int(v) for k, v in rt_obj.items()}
    except Exception as e:
        raise ValueError(f"Invalid ROLE_THRESHOLDS JSON provided (env or file): {e}")
else:
    logger.info("No ROLE_THRESHOLDS configured (no env and no mappings file)")
    ROLE_TRESHOLDS = {}
