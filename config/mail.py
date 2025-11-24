from dataclasses import dataclass
from orionis.foundation.config.mail.entities.file import File
from orionis.foundation.config.mail.entities.mail import Mail
from orionis.foundation.config.mail.entities.mailers import Mailers
from orionis.foundation.config.mail.entities.smtp import Smtp
from orionis.services.environment.env import Env

@dataclass
class BootstrapMail(Mail):

    # -------------------------------------------------------------------------
    # default : str
    #    - The default mailer transport to use.
    #    - Defaults to "smtp".
    # -------------------------------------------------------------------------
    default : str = Env.get('MAIL_MAILER', 'smtp')

    # -------------------------------------------------------------------------
    # mailers : Mailers | dict
    #    - A collection of available mail transport configurations.
    #    - Defaults to an instance of Mailers with default values if not set.
    # -------------------------------------------------------------------------
    mailers: Mailers | dict = Mailers(

        # ---------------------------------------------------------------------
        # smtp : Smtp
        #    - Configuration for the SMTP mail transport.
        #    - Defaults to environment variable values or sensible defaults.
        # ---------------------------------------------------------------------
        smtp = Smtp(
            url = Env.get('MAIL_URL', ''),
            host = Env.get('MAIL_HOST', ''),
            port = Env.get('MAIL_PORT', 587),
            encryption = Env.get('MAIL_ENCRYPTION', 'TLS'),
            username = Env.get('MAIL_USERNAME', ''),
            password = Env.get('MAIL_PASSWORD', ''),
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