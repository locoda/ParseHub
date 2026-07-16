from ...provider_api.threads import ThreadsAPI, ThreadsAPIError, ThreadsMedia, ThreadsMediaType, ThreadsPost
from ...types import AnyMediaRef, ImageRef, MultimediaParseResult, ParseError, Platform, VideoRef
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

    async def _parse(self, url: str) -> ThreadsPost:
        # Threads 现在需要登录态才能获取帖子, 因此始终带上已配置的 Cookie
        try:
            api = ThreadsAPI(proxy=self.proxy, cookie=self.cookie.get_value() if self.cookie else None)
            return await api.parse(url)
        except ThreadsAPIError as e:
            if not self.cookie:
                raise ParseError("无法获取帖子内容: Threads 需要登录, 请为 threads 平台配置 Cookie") from e
            raise ParseError("无法获取帖子内容(可能为私人或受限内容, 或 Cookie 已失效)") from e
        except ParseError:
            raise
        except Exception as e:
            raise ParseError(f"无法获取帖子内容: {e}") from e


__all__ = ["ThreadsParser"]
