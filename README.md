# xblock-video

[![Build Status](https://img.shields.io/circleci/project/raccoongang/xblock-video/dev.svg)](https://circleci.com/gh/raccoongang/xblock-video/tree/dev)
[![Coverage Status](https://img.shields.io/codecov/c/github/raccoongang/xblock-video/dev.svg)](https://codecov.io/gh/raccoongang/xblock-video)
[![GitHub release](https://img.shields.io/github/release/raccoongang/xblock-video.svg)](https://github.com/raccoongang/xblock-video/releases)

The Video XBlock is for embedding videos hosted on different video platforms
into your Open edX courses.

The idea of crowd-funded universal video-xblock was proposed by @natea
(Appsembler) at the Open edX Conference 2016 at Stanford. It was well-received
and several companies offered to sponsor the initial development.

Appsembler initially contracted with Raccoon Gang to build the [wistia-xblock]
as a prototype ([see the Github repo]), and later created a new Video XBlock
featuring universal pluggable interface with several video hosting providers
support:

[wistia-xblock]: https://appsembler.com/blog/why-open-edx-needs-an-alternative-video-xblock/
[see the Github repo]: https://github.com/appsembler/xblock-wistia

- Brightcove
- Html5
- Vimeo
- Wistia
- Youtube

Appsembler and Raccoon Gang will be co-presenting [a talk about the
video-xblock] at the Open edX Con 2017 in Madrid.

[a talk about the video-xblock]: https://openedx2017.sched.com/event/9zf6/lightning-talks

We welcome folks from the Open edX community to contribute additional video
backends as well as report and fix issues.

Thanks to [InterSystems](http://www.intersystems.com) and [Open University](http://www.open.ac.uk) for sponsoring the initial version of the Video XBlock!

## Installation

```shell
sudo -sHu edxapp
source ~/edxapp_env
# Install VideoXBlock using pip
pip install --process-dependency-links -e "git+https://github.com/raccoongang/xblock-video.git@dev#egg=video_xblock"
```

## Enabling in Studio

You can enable the Video xblock in studio through the advanced
settings:

1. From the main page of a specific course, click on *Settings*,
   *Advanced Settings* in the top menu.
1. Check for the *Advanced Module List* policy key, and add
   `"video_xblock"` in the policy value list.
   ![Advanced Module List](doc/img/advanced_settings.png)

1. Click on the *Save changes* button.

## Usage

To embed a video simply copy & paste it's URL into a `Video URL` field.

Sample supported video URLs:

- Brightcove: https://studio.brightcove.com/products/videocloud/media/videos/12345678 or https://studio.brightcove.com/products/videos/12345678
- HTML5: https://example.com/video.mpeg|mp4|ogg|webm
- Vimeo: https://vimeo.com/abcd1234
- Wistia: https://raccoongang.wistia.com/medias/xmpqebzsya
- Youtube: https://www.youtube.com/watch?v=3_yD_cEKoCk and others.

### Brightcove

To successfully use videos hosted on Brightcove Videocloud service one must provide valid Brightcove `account_id` associated with the video. One can find

#### Connect to Brightcove Platform

1. Grab your [BC_TOKEN] from Brightcove Videocloud.
1. Open Video XBlock settings, Advanced tab. Scroll down to `Video API Token` section.
1. Put `BC_TOKENT` taken from Brightcvove into `Client Token` field.
1. Click on `Connect to video platform` button.

[BC_TOKEN]: https://docs.brightcove.com/en/video-cloud/media-management/guides/authentication.html

#### Enable content encryption and/or autoquality

Given you've connected XBlock to Brightcove platform and have a Video XBlock with a video from Brightcove. You can enablevideo content encryption and/or auto-quality.

To do so:
1. Go to Advanced settings tab.
1. Scroll down to `Brightcove content protection` section.
1. Select `Autoquality` or `Autoquality & Encryption`.
1. Click `Re-transcode this video` button.

Re-transcode is performed by Brightcove's Videocloud and takes few minutes. After it's done `Brightcove Video tech info` section will be updated.

### Set default values in config files

Sample default settings in `/edx/app/edxapp/cms.env.json`:

```json
    "XBLOCK_SETTINGS": {
      "video_xblock": {
        "threeplaymedia_apikey": "987654321",
        "account_id": "1234567890"
      }
    }
```

## Development

Prereqs: [NodeJS >= 4.0](https://docs.npmjs.com/getting-started/installing-node#updating-npm)

Install development tools and dependencies:

```shell
> make tools deps-test
```

Run quality checks:

```shell
> make quality
```

Run tests:

```shell
> make test
```

VideoXBlock is bundled with a set of XBlock-SDK Workbench scenarios.
See [workbench docs](/video_xblock/workbench/README.md) for details.

## License

The code in this repository is licensed under the GPL v3 licence unless
otherwise noted.

Please see `LICENSE` file for details.
