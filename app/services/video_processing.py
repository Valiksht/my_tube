"""Обработка видео через FFmpeg.

Создание превью, проверка формата, извлечение метаданных.
Запускается асинхронно через asyncio.create_subprocess_exec.
"""

import asyncio
import os
import re
from pathlib import Path
from typing import Optional


class VideoProcessor:
    """Обработчик видео через FFmpeg."""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe"):
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path
    
    async def get_video_info(self, file_path: str) -> dict:
        """Получить информацию о видео через ffprobe.
        
        Args:
            file_path: Путь к видео файлу.
            
        Returns:
            Словарь с метаданными видео.
        """
        try:
            cmd = [
                self.ffprobe_path,
                "-v", "error",
                "-show_entries", "format=duration,size,bit_rate",
                "-show_entries", "stream=width,height,codec_name,r_frame_rate,codec_type",
                "-of", "json",
                file_path,
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                raise RuntimeError(f"ffprobe error: {stderr.decode()}")
            
            import json
            info = json.loads(stdout)
            
            # Извлекаем видео поток
            video_stream = None
            audio_stream = None
            
            for stream in info.get("streams", []):
                if stream.get("codec_type") == "video":
                    video_stream = stream
                elif stream.get("codec_type") == "audio":
                    audio_stream = stream
            
            # Парсим длительность
            duration = None
            if "format" in info and "duration" in info["format"]:
                duration = float(info["format"]["duration"])
            
            return {
                "duration": duration,
                "width": video_stream.get("width") if video_stream else None,
                "height": video_stream.get("height") if video_stream else None,
                "video_codec": video_stream.get("codec_name") if video_stream else None,
                "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
                "size": info.get("format", {}).get("size"),
                "bit_rate": info.get("format", {}).get("bit_rate"),
            }
            
        except FileNotFoundError:
            raise RuntimeError("FFmpeg не найден. Установите FFmpeg в систему.")
    
    async def create_thumbnail(
        self,
        file_path: str,
        output_path: str,
        timestamp: float = 1.0,
    ) -> str:
        """Создать превью видео.
        
        Args:
            file_path: Путь к видео файлу.
            output_path: Путь для сохранения превью.
            timestamp: Время в секундах для захвата кадра.
            
        Returns:
            Путь к созданному превью.
        """
        try:
            # Создаём директорию если не существует
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            cmd = [
                self.ffmpeg_path,
                "-y",  # Перезаписать файл
                "-i", file_path,
                "-ss", str(timestamp),  # Время захвата
                "-vframes", "1",  # Один кадр
                "-q:v", "2",  # Качество (меньше = лучше)
                output_path,
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg error: {stderr.decode()}")
            
            return output_path
            
        except FileNotFoundError:
            raise RuntimeError("FFmpeg не найден.")
    
    async def validate_video(self, file_path: str) -> bool:
        """Проверить что файл является валидным видео.
        
        Args:
            file_path: Путь к файлу.
            
        Returns:
            True если валидное видео.
        """
        try:
            info = await self.get_video_info(file_path)
            
            # Проверяем что есть видео поток
            if not info.get("video_codec"):
                return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def get_allowed_extensions() -> list:
        """Получить список допустимых расширений."""
        return [".mp4", ".webm", ".ogg", ".mkv", ".avi", ".mov"]
    
    @staticmethod
    def get_allowed_codecs() -> list:
        """Получить список допустимых видео кодеков."""
        return ["h264", "vp8", "vp9", "mpeg4", "theora"]


# Глобальный экземпляр
video_processor = VideoProcessor()
