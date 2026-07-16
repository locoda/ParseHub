from ...provider_api.threads import ThreadsAPI, ThreadsMedia, ThreadsMediaType, ThreadsPost
from ...types import AnyMediaRef, ImageRef, MultimediaParseResult, ParseError, Platform, VideoRef
from ...utils.helpers import SecretCookie
from ..base.base import BaseParser


class ThreadsParser(BaseParser):
    __platform__ = Platform.THREADS
    __supported_type__ = ["视频", "图文"]
    __match__ = r"^(http(s)?://)?.+threads.com/@[\w.]+/post/.*"

    async def _do_parse(self, raw_url: str) -> "MultimediaParseResult":
        post = await self._parse(raw_url)
        media: list[AnyMediaRef] = []
        if post.media:
            pm: list[ThreadsMedia] = post.media if isinstance(post.media, list) else [post.media]
            for m in pm:
                match m.type:
                    case ThreadsMediaType.VIDEO:
                        media.append(VideoRef(url=m.url, thumb_url=m.thumb_url, width=m.width, height=m.height))
                    case ThreadsMediaType.IMAGE:
                        media.append(ImageRef(url=m.url, thumb_url=m.url, width=m.width, height=m.height))
        return MultimediaParseResult(content=post.content, media=media)

    async def _parse(self, url: str, cookie: SecretCookie | None = None) -> ThreadsPost:
        try:
            api = ThreadsAPI(proxy=self.proxy, cookie=cookie.get_value() if cookie else None)
            return await api.parse(url)
        except Exception as e:
            # 未登录时对私密/受限内容会失败, 若已配置 Cookie 则带上 Cookie 重试一次
            if self.cookie and cookie is None:
                return await self._parse(url, self.cookie)
            raise ParseError("无法获取帖子内容(可能为私人或受限内容)") from e


__all__ = ["ThreadsParser"]
