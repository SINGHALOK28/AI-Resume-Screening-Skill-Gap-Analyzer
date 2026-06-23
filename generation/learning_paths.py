"""Learning path recommendations for missing skills."""

from typing import Dict, List

LEARNING_RESOURCES: Dict[str, List[Dict]] = {
    "python": [
        {"title": "Python Official Tutorial", "url": "https://docs.python.org/3/tutorial/", "type": "docs"},
        {"title": "freeCodeCamp Python", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "type": "course"},
    ],
    "javascript": [
        {"title": "MDN JavaScript Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "type": "docs"},
        {"title": "freeCodeCamp JS", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "type": "course"},
    ],
    "react": [
        {"title": "React Official Docs", "url": "https://react.dev/learn", "type": "docs"},
    ],
    "sql": [
        {"title": "SQLBolt", "url": "https://sqlbolt.com/", "type": "course"},
        {"title": "Mode SQL Tutorial", "url": "https://mode.com/sql-tutorial/", "type": "course"},
    ],
    "machine learning": [
        {"title": "scikit-learn Tutorials", "url": "https://scikit-learn.org/stable/tutorial/index.html", "type": "docs"},
        {"title": "fast.ai Practical Deep Learning", "url": "https://course.fast.ai/", "type": "course"},
    ],
    "docker": [
        {"title": "Docker Getting Started", "url": "https://docs.docker.com/get-started/", "type": "docs"},
    ],
    "kubernetes": [
        {"title": "Kubernetes Basics", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "type": "docs"},
    ],
    "aws": [
        {"title": "AWS Skill Builder", "url": "https://skillbuilder.aws/", "type": "course"},
    ],
    "default": [
        {"title": "Search on Coursera/edX", "url": "https://www.coursera.org/", "type": "course"},
    ],
}


def get_learning_paths(missing_skills: List[str], max_per_skill: int = 2) -> List[Dict]:
    """Return learning resources for each missing skill."""
    paths = []
    for skill in missing_skills[:10]:
        key = skill.lower()
        resources = LEARNING_RESOURCES.get(key, LEARNING_RESOURCES["default"])[:max_per_skill]
        paths.append({
            "skill": skill,
            "resources": resources,
        })
    return paths
