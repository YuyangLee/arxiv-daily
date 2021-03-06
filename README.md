# Arxiv Daily

Download papers from arxiv according to your subscriptions and filter keywords.

## Basic Usage

Typically you just install the requirements specified in `requirements.txt` by:

```shell
pip install -r requirements.txt
```

Then just run `python run.py` with your arguments.

### Subscriptions

Modify `data/subs.json` to customize your subscriptions. You should specify the categories (both category and sub-category) and filtering keywords you want to subscribe to.

Eg. Alice want to subscribe to something about NeRF in `cs.CV`, as well as some robotic tasks like reorientation in `cs.RO`. The `subs.json` should be like:

```json
{
    "subs": [
        [
            "cs", "CV",
            [
                "Neural Radiance Field",
                "NeRF"
            ]
        ],
        [
            "cs", "RO",
            [
                "Reorientation"
            ]
        ]
    ]
}
```

> It doesn't matter whether you write the letters in upper or lower case.

### Modifying Schedule

You can modify the paper fetching schedule by modifying `cron` rules of `apscheduler` in `run.py`. By default the program load your subscriptions and fetch papers everyday at 6 am.

### Notion API

PENDING...

### Send to Drives

Please use [RCLONE](https://rclone.org/) to mount your cloud storage on your machine. Then by adding argument `--dispatch true` and specifying `--dispatch_dir YOUR_DIRECTORY` the archived package will be sent to the directory after archiving.

# Credits

This small project was made possible by these repos:

- [Tachyu/Arxiv-download](https://github.com/Tachyu/Arxiv-download)