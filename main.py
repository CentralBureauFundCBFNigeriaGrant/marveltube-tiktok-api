import os
from fastapi import FastAPI, HTTPException
from TikTokApi import TikTokApi
import uvicorn
import asyncio

# Explicitly tell Playwright where the browser binaries are located in the Docker image
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/ms-playwright'

app = FastAPI()

@app.get("/get-video")
async def get_video(handle: str):
    try:
        async with TikTokApi() as api:
            # headless=True with the Playwright Docker image works perfectly
            await api.create_sessions(num_sessions=1, headless=True)
            user = api.user(username=handle)
            user_data = await user.info()
            if not user_data:
                raise HTTPException(status_code=404, detail="User not found")
            
            videos = []
            async for video in user.videos(count=10):
                videos.append({
                    "id": video.id,
                    "url": f"https://www.tiktok.com/@{handle}/video/{video.id}",
                    "play_count": video.stats.play_count
                })
            
            if not videos:
                raise HTTPException(status_code=404, detail="No videos found")
            
            viral_video = max(videos, key=lambda v: v['play_count'])
            return {"video_url": viral_video['url'], "id": viral_video['id']}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port="8000")
