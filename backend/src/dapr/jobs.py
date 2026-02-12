"""Dapr Jobs API client wrapper for exact-time scheduling."""

import httpx
from typing import Any, Dict, Optional
from datetime import datetime


class DaprJobsClient:
    """Client for Dapr Jobs API (alpha)."""

    def __init__(self, dapr_port: int = 3500):
        """Initialize Dapr Jobs API client.

        Args:
            dapr_port: Dapr sidecar HTTP port (default: 3500)
        """
        self.dapr_url = f"http://localhost:{dapr_port}"

    async def schedule_job(
        self,
        job_name: str,
        due_time: datetime,
        data: Dict[str, Any],
        callback_url: str = "/api/jobs/trigger"
    ) -> bool:
        """Schedule a job to fire at exact time using Dapr Jobs API.

        Args:
            job_name: Unique job identifier
            due_time: When the job should fire (exact datetime)
            data: Job payload data
            callback_url: URL that Dapr will POST to when job fires

        Returns:
            True if scheduled successfully
        """
        url = f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}"

        payload = {
            "dueTime": due_time.isoformat(),
            "data": data,
            "callback": {
                "url": callback_url,
                "method": "POST"
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    timeout=5.0
                )
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            print(f"Failed to schedule job {job_name}: {e}")
            return False

    async def cancel_job(self, job_name: str) -> bool:
        """Cancel a scheduled job.

        Args:
            job_name: Job identifier to cancel

        Returns:
            True if cancelled successfully
        """
        url = f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, timeout=5.0)
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            print(f"Failed to cancel job {job_name}: {e}")
            return False

    async def get_job(self, job_name: str) -> Optional[Dict[str, Any]]:
        """Get job details.

        Args:
            job_name: Job identifier

        Returns:
            Job details or None if not found
        """
        url = f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"Failed to get job {job_name}: {e}")
            return None

    async def schedule_reminder(
        self,
        task_id: int,
        user_id: str,
        remind_at: datetime,
        reminder_id: int
    ) -> bool:
        """Schedule a reminder using Dapr Jobs API.

        Args:
            task_id: Task ID
            user_id: User ID
            remind_at: When reminder should fire
            reminder_id: Reminder ID

        Returns:
            True if scheduled successfully
        """
        job_name = f"reminder-task-{task_id}-{reminder_id}"

        data = {
            "task_id": task_id,
            "user_id": user_id,
            "reminder_id": reminder_id,
            "type": "reminder"
        }

        return await self.schedule_job(job_name, remind_at, data)

    async def cancel_reminder(self, task_id: int, reminder_id: int) -> bool:
        """Cancel a scheduled reminder.

        Args:
            task_id: Task ID
            reminder_id: Reminder ID

        Returns:
            True if cancelled successfully
        """
        job_name = f"reminder-task-{task_id}-{reminder_id}"
        return await self.cancel_job(job_name)
