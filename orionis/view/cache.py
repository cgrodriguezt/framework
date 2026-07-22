from __future__ import annotations
from pathlib import Path
from jinja2.bccache import Bucket, FileSystemBytecodeCache

# Extensions stripped before building the cache filename
_TEMPLATE_EXTENSIONS: tuple[str, ...] = (
    ".html", ".htm", ".jinja", ".jinja2", ".j2",
)

class OrionisBytecodeCache(FileSystemBytecodeCache):

    def get_cache_key(self, name: str, filename: str | None = None) -> str: # noqa: ARG002
        """Convert a template name into a human-readable cache key.

        Parameters
        ----------
        name : str
            Template identifier (e.g. ``'users/index.html'``).
        filename : str or None, optional
            Absolute path on disk; unused here.

        Returns
        -------
        str
            Sanitised key used as the cache filename stem.
        """
        key: str = name.replace("/", ".").replace("\\", ".")
        for ext in _TEMPLATE_EXTENSIONS:
            if key.endswith(ext):
                key = key[: -len(ext)]
                break
        return key

    def _get_cache_filename(self, bucket: Bucket) -> str:
        """
        Return the absolute path to the cache file for *bucket*.

        Parameters
        ----------
        bucket : Bucket
            Jinja2 bucket whose ``key`` is the sanitised template name.

        Returns
        -------
        str
            Absolute path of the form ``<cache_dir>/<template_name>.cache``.
        """
        return str(Path(self.directory) / f"{bucket.key}.cache")
