from dataclasses import dataclass
from orionis.foundation.config.filesystems.entitites.aws import S3
from orionis.foundation.config.filesystems.entitites.disks import Disks
from orionis.foundation.config.filesystems.entitites.filesystems import Filesystems
from orionis.foundation.config.filesystems.entitites.local import Local
from orionis.foundation.config.filesystems.entitites.public import Public

@dataclass
class BootstrapFilesystems(Filesystems):

    # -------------------------------------------------------------------------
    # default : str
    #    - The name of the default filesystem disk to use.
    #    - Defaults to "local".
    # -------------------------------------------------------------------------
    default = "local"

    # -------------------------------------------------------------------------
    # disks : Disks | dict
    #    - The different filesystem disks available to the application.
    #    - Defaults to an instance of Disks with default values if not set.
    # -------------------------------------------------------------------------
    disks = Disks(

        # ---------------------------------------------------------------------
        # local : Local
        #    - Configuration for the local filesystem disk.
        #    - Defaults to storing files in "storage/app/private".
        # ---------------------------------------------------------------------
        local = Local(
            path = "storage/app/private"
        ),

        # ---------------------------------------------------------------------
        # public : Public
        #    - Configuration for the public filesystem disk.
        #    - Defaults to storing files in "storage/app/public" and serving them from "static".
        # ---------------------------------------------------------------------
        public = Public(
            path = "storage/app/public",
            url = "/static"
        ),

        # ---------------------------------------------------------------------
        # aws : S3
        #    - Configuration for the AWS S3 filesystem disk.
        #    - Defaults to empty values; must be configured with valid credentials and settings.
        # ---------------------------------------------------------------------
        aws = S3(
            key = "",
            secret = "",
            region = "us-east-1",
            bucket = "",
            url = None,
            endpoint = None,
            use_path_style_endpoint = False,
            throw = False
        )
    )