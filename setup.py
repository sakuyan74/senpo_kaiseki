from setuptools import setup, find_packages

setup(
    name="senpo_kaiseki",
    version="1.0",
    description="戦報画像を解析してエクセルに登録する",
    author="sakuyan74",
    author_email="ginkou74@yahoo.co.jp",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "senpo_kaiseki = senpo_kaiseki.main:main"
        ]
    }
)
