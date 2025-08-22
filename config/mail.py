from dataclasses import dataclass, field, fields
from orionis.foundation.config.mail.entities.file import File
from orionis.foundation.config.mail.entities.mail import Mail
from orionis.foundation.config.mail.entities.mailers import Mailers
from orionis.foundation.config.mail.entities.smtp import Smtp

@dataclass
class BootstrapMail(Mail):

    # -------------------------------------------------------------------------
    # default : str
    #    - The default mailer transport to use.
    #    - Defaults to "smtp".
    # -------------------------------------------------------------------------
    default = "smtp"

    # -------------------------------------------------------------------------
    # mailers : Mailers | dict
    #    - A collection of available mail transport configurations.
    #    - Defaults to an instance of Mailers with default values if not set.
    # -------------------------------------------------------------------------
    mailers = Mailers(

        # ---------------------------------------------------------------------
        # smtp : Smtp
        #    - Configuration for the SMTP mail transport.
        #    - Defaults to a Mailtrap SMTP configuration.
        # ---------------------------------------------------------------------
        smtp = Smtp(
            url = "smtp.mailtrap.io",
            host = "smtp.mailtrap.io",
            port = 587,
            encryption = "TLS",
            username = "",
            password = "",
            timeout = None
        ),

        # ---------------------------------------------------------------------
        # file : File
        #    - Configuration for the file mail transport.
        #    - Defaults to storing emails in "storage/mail" directory.
        # ---------------------------------------------------------------------
        file = File(
            path = "storage/mail"
        )
    )