from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.filesystems.entitites.aws import S3
from orionis.foundation.config.filesystems.entitites.disks import Disks
from orionis.foundation.config.filesystems.entitites.filesystems import Filesystems
from orionis.foundation.config.filesystems.entitites.local import Local
from orionis.foundation.config.filesystems.entitites.public import Public
from orionis.services.environment.env import Env

@dataclass(frozen=True, kw_only=True)
class BootstrapFilesystems(Filesystems):

    # ----------------------------------------------------------------------------------
    # default : str, optional
    # --- Sets the default filesystem disk name.
    # --- Uses 'FILESYSTEM_DISK' env var or 'local' if not set.
    # ----------------------------------------------------------------------------------

    default: str = field(
        default_factory=lambda: Env.get("FILESYSTEM_DISK", "local"),
    )

    # ----------------------------------------------------------------------------------
    # disks : Disks | dict, optional
    # --- Holds available filesystem disks for the app.
    # --- Defaults to Disks with local, public, and AWS S3 configs.
    # ----------------------------------------------------------------------------------

    disks: Disks | dict = field(
        default_factory=lambda: Disks(

            # --------------------------------------------------------------------------
            # --- Local disk stores files in 'storage/app/private'.
            # --- Uses Local entity for private file storage path.
            # --- Defaults to 'storage/app/private' if not set.
            # --------------------------------------------------------------------------
            local=Local(
                path="storage/app/private",
            ),

            # --------------------------------------------------------------------------
            # --- Public disk stores files in 'storage/app/public'.
            # --- Uses Public entity for storage path and public URL.
            # --- Defaults to 'storage/app/public' and serves from '/static'.
            # --------------------------------------------------------------------------
            public=Public(
                path="storage/app/public",
                url="/static",
            ),

            # --------------------------------------------------------------------------
            # --- AWS S3 disk uses S3 entity for cloud storage.
            # --- Defaults to empty credentials and 'us-east-1' region.
            # --- Path style endpoint is disabled by default.
            # --------------------------------------------------------------------------
            aws=S3(
                key="",
                secret="",
                region="us-east-1",
                bucket="",
                url=None,
                endpoint=None,
                use_path_style_endpoint=False,
                throw=False,
            ),

        ),
    )
