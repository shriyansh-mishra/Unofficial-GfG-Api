import re
import json
import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class GeeksforGeeksScraper:

    BASE_URL = "https://www.geeksforgeeks.org/user/"

    def __init__(self):
        """Initialize the scraper with default headers and session"""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": os.getenv("USER_AGENT", "Default User-Agent"),
                "Accept": os.getenv("ACCEPT", "*/*"),
                "Accept-Language": os.getenv("ACCEPT_LANGUAGE", "en-US"),
                "Referer": os.getenv("REFERER", "https://www.geeksforgeeks.org/"),
                "DNT": os.getenv("DNT", "1"),
            }
        )

    def _get_profile_data(self, username):
        
        url = f"{self.BASE_URL}{username}/"
        logger.debug(f"Fetching profile from URL: {url}")

        try:
            response = self.session.get(url, timeout=10)

            match = re.search(
                r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                response.text,
                re.DOTALL,
            )
            if not match:
                raise Exception(
                    f"Could not find Next.js data in the profile page for '{username}'"
                )

            json_data = match.group(1)
            data = json.loads(json_data)

            if "Profile does not exist" in response.text:
                raise Exception(f"Profile '{username}' does not exist")

            return data

        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Failed to fetch profile: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {str(e)}")
            raise Exception(f"Failed to parse profile data: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    def get_complete_profile(self, username):
        
        profile_data = self._get_profile_data(username)

        user_info = self._extract_user_info(profile_data, username)
        coding_stats = self._extract_next_coding_stats(profile_data)
        difficulty_stats = self._extract_next_difficulty_stats(
            profile_data, include_problems=True
        )
        institution_languages = self._extract_next_institution_languages(profile_data)
        streak_data = self._extract_next_streak(profile_data)

        complete_profile = {
            "info": {
                "username": user_info.get("username"),
                "fullname": user_info.get("fullname"),
                "qualification": user_info.get("qualification"),
                "joined_date": user_info.get("joined_date"),
                "institution": institution_languages.get("institution"),
                "languages_used": institution_languages.get("languages_used"),
            },
            "solved_stats": {
                "coding_score": coding_stats.get("coding_score"),
                "problems_solved": coding_stats.get("problems_solved"),
                "contest_rating": coding_stats.get("contest_rating"),
                "overall_rank": coding_stats.get("overall_rank"),
                "total_submissions": coding_stats.get("problems_solved"),
                "monthly_score": streak_data.get("monthly_score"),
                "current_streak": streak_data.get("current_streak"),
                "longest_streak": streak_data.get("longest_streak"),
                "difficulty_breakdown": difficulty_stats.get("solved_by_difficulty"),
                "problems_by_difficulty": difficulty_stats.get(
                    "problems_by_difficulty", {}
                ),
            },
        }

        return complete_profile

    def get_basic_info(self, username):
        
        profile_data = self._get_profile_data(username)
        return self._extract_user_info(profile_data, username)

    def _extract_user_info(self, profile_data, username):
        
        basic_info = {"username": username, "qualification": None, "fullname": None}

        try:
            user_info = (
                profile_data.get("props", {}).get("pageProps", {}).get("userInfo", {})
            )

            if user_info:
                if "name" in user_info:
                    basic_info["fullname"] = user_info.get("name")

                if "institute_name" in user_info:
                    basic_info["qualification"] = user_info.get("institute_name")

                if "created_date" in user_info:
                    basic_info["joined_date"] = user_info.get("created_date")


        except Exception as e:
            logger.error(f"Error extracting basic info: {str(e)}")

        return basic_info

    def get_coding_stats(self, username):
        
        profile_data = self._get_profile_data(username)
        return self._extract_next_coding_stats(profile_data)

    def _extract_next_coding_stats(self, profile_data):
        
        coding_stats = {
            "coding_score": None,
            "problems_solved": None,
            "contest_rating": None,
            "overall_rank": None,
        }

        try:
            user_info = (
                profile_data.get("props", {}).get("pageProps", {}).get("userInfo", {})
            )

            if user_info:
                if "score" in user_info:
                    coding_stats["coding_score"] = user_info.get("score")

                if "total_problems_solved" in user_info:
                    coding_stats["problems_solved"] = user_info.get(
                        "total_problems_solved"
                    )

                contest_data = (
                    profile_data.get("props", {})
                    .get("pageProps", {})
                    .get("contestData", {})
                )
                if contest_data:
                    user_contest_data = contest_data.get("user_contest_data", {})
                    if user_contest_data and "current_rating" in user_contest_data:
                        coding_stats["contest_rating"] = user_contest_data.get(
                            "current_rating"
                        )

                    if "user_global_rank" in contest_data:
                        coding_stats["overall_rank"] = contest_data.get(
                            "user_global_rank"
                        )

        except Exception as e:
            logger.error(f"Error extracting coding stats: {str(e)}")

        return coding_stats

    def get_submission_data(self, username):
        
        profile_data = self._get_profile_data(username)
        return self._extract_next_submission_data(profile_data)

    def _extract_next_submission_data(self, profile_data):
        
       
        submission_data = {
            "total_submissions": None,
            "monthly_problems_solved": None,
            "submissions_by_difficulty": {
                "basic": [],
                "easy": [],
                "medium": [],
                "hard": [],
            },
        }

        try:
            user_info = (
                profile_data.get("props", {}).get("pageProps", {}).get("userInfo", {})
            )

            if user_info:
                if "total_problems_solved" in user_info:
                    submission_data["total_submissions"] = user_info.get(
                        "total_problems_solved"
                    )

                if "monthly_score" in user_info:
                    submission_data["monthly_problems_solved"] = user_info.get(
                        "monthly_score"
                    )

            user_submissions = (
                profile_data.get("props", {})
                .get("pageProps", {})
                .get("userSubmissionsInfo", {})
            )

            for difficulty, key in [
                ("Basic", "basic"),
                ("Easy", "easy"),
                ("Medium", "medium"),
                ("Hard", "hard"),
            ]:
                if difficulty in user_submissions:
                    submissions = user_submissions[difficulty]
                    if submissions:
                        for problem_id, problem_data in submissions.items():
                            if problem_data:
                                problem_name = problem_data.get("pname", "")
                                problem_slug = problem_data.get("slug", "")

                                if not problem_name or not problem_slug:
                                    continue

                                problem_url = f"https://practice.geeksforgeeks.org/problems/{problem_slug}/0"

                                submission_data["submissions_by_difficulty"][
                                    key
                                ].append({"name": problem_name, "url": problem_url})

        except Exception as e:
            logger.error(f"Error extracting submission data: {str(e)}")

        return submission_data

    def get_difficulty_stats(self, username):
       
        profile_data = self._get_profile_data(username)
        return self._extract_next_difficulty_stats(profile_data)

    def _extract_next_difficulty_stats(self, profile_data, include_problems=False):
        
        difficulty_stats = {
            "solved_by_difficulty": {"basic": 0, "easy": 0, "medium": 0, "hard": 0}
        }

        if include_problems:
            difficulty_stats["problems_by_difficulty"] = {
                "basic": [],
                "easy": [],
                "medium": [],
                "hard": [],
            }

        try:
            user_submissions = (
                profile_data.get("props", {})
                .get("pageProps", {})
                .get("userSubmissionsInfo", {})
            )

            for difficulty, key in [
                ("Basic", "basic"),
                ("Easy", "easy"),
                ("Medium", "medium"),
                ("Hard", "hard"),
            ]:
                if difficulty in user_submissions:
                    submissions = user_submissions[difficulty]
                    difficulty_stats["solved_by_difficulty"][key] = len(submissions)

                    if include_problems and submissions:
                        for problem_id, problem_data in submissions.items():
                            if problem_data:
                                problem_name = problem_data.get("pname", "")
                                problem_slug = problem_data.get("slug", "")

                                if not problem_name or not problem_slug:
                                    continue

                                problem_url = f"https://www.geeksforgeeks.org/problems/{problem_slug}/0"

                                difficulty_stats["problems_by_difficulty"][key].append(
                                    {"name": problem_name, "url": problem_url}
                                )

        except Exception as e:
            logger.error(f"Error extracting difficulty stats: {str(e)}")

        return difficulty_stats

    def get_institution_languages(self, username):
        
        profile_data = self._get_profile_data(username)
        return self._extract_next_institution_languages(profile_data)

    def _extract_next_institution_languages(self, profile_data):
        
        institution_languages = {"institution": None, "languages_used": []}

        try:
            # Extract data from userInfo in Next.js data
            user_info = (
                profile_data.get("props", {}).get("pageProps", {}).get("userInfo", {})
            )

            if user_info:
                if "institute_name" in user_info:
                    institution_languages["institution"] = user_info.get(
                        "institute_name"
                    )

            languages_str = (
                profile_data.get("props", {}).get("pageProps", {}).get("languages")
            )
            if languages_str:
                languages = [lang.strip() for lang in languages_str.split(",")]
                institution_languages["languages_used"] = languages

        except Exception as e:
            logger.error(f"Error extracting institution and languages: {str(e)}")

        return institution_languages

    def get_streak(self, username):
        
        profile_data = self._get_profile_data(username)
        return self._extract_next_streak(profile_data)

    def _extract_next_streak(self, profile_data):
        
        streak_data = {
            "current_streak": None,
            "longest_streak": None,
            "monthly_score": None,
        }

        try:
            user_info = (
                profile_data.get("props", {}).get("pageProps", {}).get("userInfo", {})
            )

            if user_info:
                if "monthly_score" in user_info:
                    streak_data["monthly_score"] = user_info.get("monthly_score")

                if "pod_solved_longest_streak" in user_info:
                    streak_data["longest_streak"] = user_info.get(
                        "pod_solved_longest_streak"
                    )

                heat_map_data = (
                    profile_data.get("props", {})
                    .get("pageProps", {})
                    .get("heatMapData", {})
                    .get("result", {})
                )
                if heat_map_data:
                    dates = sorted(heat_map_data.keys(), reverse=True)
                    current_streak = 0

                    for i, date in enumerate(dates):
                        if i > 0:
                            if heat_map_data.get(date):
                                current_streak += 1
                            else:
                                break
                        elif heat_map_data.get(date):
                            current_streak = 1

                    if current_streak > 0:
                        streak_data["current_streak"] = current_streak

        except Exception as e:
            logger.error(f"Error extracting streak data: {str(e)}")

        return streak_data
