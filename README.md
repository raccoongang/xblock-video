# xblock-video

[![Build Status](https://img.shields.io/circleci/project/raccoongang/xblock-video/dev.svg)](https://circleci.com/gh/raccoongang/xblock-video/tree/dev)
[![Coverage Status](https://img.shields.io/codecov/c/github/raccoongang/xblock-video/dev.svg)](https://codecov.io/gh/raccoongang/xblock-video)
[![GitHub release](https://img.shields.io/github/release/raccoongang/xblock-video.svg)](https://github.com/raccoongang/xblock-video/releases)

The Video XBlock is for embedding videos hosted on different video platforms
into your Open edX courses.

Supported video platforms:

- Brightcove
- Html5
- Tencent
- Vimeo
- Wistia
- Youtube

The idea of crowd-funded universal video-xblock was proposed by @natea
(Appsembler) at the Open edX Conference 2016 at Stanford. It was well-received
and several companies offered to sponsor the initial development.

Appsembler initially contracted with Raccoon Gang to build the [wistia-xblock]
as a prototype ([see the Github repo]), and later created a new Video XBlock
featuring universal pluggable interface with several video hosting providers
support:

[wistia-xblock]: https://appsembler.com/blog/why-open-edx-needs-an-alternative-video-xblock/
[see the Github repo]: https://github.com/appsembler/xblock-wistia

Appsembler and Raccoon Gang presented [a talk about the
video-xblock] at the Open edX Con 2017 in Madrid.

[a talk about the video-xblock]: https://openedx2017.sched.com/event/9zf6/lightning-talks

We welcome folks from the Open edX community to contribute additional video
backends as well as report and fix issues.

Thanks to [InterSystems] and [Open University] for sponsoring the initial
version of the Video XBlock!

[InterSystems]: https://www.intersystems.com
[Open University]: https://www.open.ac.uk

## Installation

```shell
sudo -sHu edxapp
source ~/edxapp_env
# Install VideoXBlock using pip
pip install git+https://github.com/raccoongang/xblock-video.git@master#egg=video_xblock
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

To embed a video simply copy & paste its URL into a `Video URL` field.

Sample supported video URLs:

- Brightcove: https://studio.brightcove.com/products/videocloud/media/videos/12345678 or https://studio.brightcove.com/products/videos/12345678
- HTML5: https://example.com/video.mpeg|mp4|ogg|webm
- Vimeo: https://vimeo.com/773500743
- Wistia: https://raccoongang.wistia.com/medias/xmpqebzsya
- Youtube: https://www.youtube.com/watch?v=3_yD_cEKoCk and others.

### Vimeo

Vimeo is an online video platform that allows users to upload, view, and share videos.
It is designed for storing and publishing professional and user-generated video content,
including films, music videos, video tutorials, and much more. Vimeo offers both free
and paid subscriptions, depending on how users want to use the platform.

There is a known issue related to the subtitles/transcripts' functionality.
The Vimeo player will only display subtitles uploaded through the Vimeo platform account
web page. To allow users to download Vimeo subtitles you'll need the Vimeo API key added
to the x-block advanced settings. Transcripts uploaded through the Studio for the video
block can be used only for download.

### Brightcove

To successfully use videos hosted on Brightcove Videocloud service one must
provide valid Brightcove `account_id` associated with the video. To find out
your `account_id` go to [Videocloud studio] -> _Admin_ -> _Account Information_.

Currently, Brightcove does not provide a free account for working with their service.
A trial account is available for one month and can be activated with the help of
their support team. At the moment, RG does not have an account that would allow
updating and testing the functionality of the Video X-Block with the Brightcove service.
Our Video X-Block is integrated with the Brightcove service, but we cannot
test certain features associated with it. As a result, we cannot guarantee error-free
usage of this provider.

[Videocloud studio]: https://studio.brightcove.com/products/videocloud/home

#### Connect to Brightcove Platform

1. Grab your [BC_TOKEN] from Brightcove Videocloud:
   1. Login to [Videocloud Studio] as you normally do.
   2. With any page in Studio open, open the developer tools for the browser,
      go to the Console, and paste in the following code:

   ```js
       var cookiesArray = document.cookie.split(";"), cookiesObj = {}, i, tmpArray = [];
       for (i = 0; i < cookiesArray.length; i++) {
           tmpArray = cookiesArray[i].split("=");
           if (tmpArray[0].indexOf('BC_TOKEN') > -1) {
               cookiesObj.BC_TOKEN = tmpArray[1];
           }
       }
       window.prompt("BC_TOKEN:", cookiesObj.BC_TOKEN);
   ```
   and press `<return>`.

   3. You should see a prompt appear that contains your BC_TOKEN.
    ![BC_TOKEN sample](https://learning-services-media.brightcove.com/doc-assets/video-cloud-apis/ingest-profiles-api/guides/prompt-with-token-safari.png "Sample BC_TOKEN")
1. Open Video XBlock settings, Advanced tab. Scroll down to `Video API Token` section.
1. Put `BC_TOKEN` taken from Brightcvove into `Client Token` field.
1. Click on `Connect to video platform` button.

[Videocloud Studio]: https://studio.brightcove.com/products/videocloud/home
[BC_TOKEN]: https://docs.brightcove.com/en/video-cloud/media-management/guides/authentication.html

#### Enable content encryption and/or autoquality

Given you've connected XBlock to Brightcove platform and have a Video XBlock with a video from Brightcove. You can enablevideo content encryption and/or auto-quality.

To do so:
1. Go to Advanced settings tab.
1. Scroll down to `Brightcove content protection` section.
1. Select `Autoquality` or `Autoquality & Encryption`.
1. Click `Re-transcode this video` button.

Re-transcode is performed by Brightcove's Videocloud and takes few minutes. After it's done `Brightcove Video tech info` section will be updated.

### Tencent

TencentPlayer is used for videos hosted on tencent cloud.
To test this player, you need to create a Tencent test account in the cloud.
But to register for this service, you need to link a card and pass verification.

Internal RG tickets with the testing outputs:
- [initial implementation and testing](https://youtrack.raccoongang.com/issue/HARROW-976)
- [RGOeX-25789](https://youtrack.raccoongang.com/issue/RGOeX-25789).

Note: [Tencent Cloud Documentation](https://www.tencentcloud.com/document/product)

### Wistia

It is currently possible to use the Wistia provider in Video XBlock.
However, to fully test all the functionality of the XBlock when working
with this provider, a paid Wistia account is required. RG does not have 
such an account. Therefore, we are unable to test the functionality of
transcripts that are connected to videos in the Wistia studio.

Note: There have been [changes](https://wistia.com/support/developers/wistia-deprecation-schedule)
in the provision of API at this provider.

#### Connect to Wistia Platform

1. Create a Wistia account and create an app. Copy the API Token in the settings.
1. Write the API Token in the Client Token field in the X-Block settings.
1. Uploading a video and transcripts to the Wistia service.

#### How to disable captions auto uploading in Wistia plugin

1. Open your Project in Wistia Platform.
1. Open video which you want to use with Video XBlock.
1. Click the `Video Actions` drop-down menu -> Select the `Customize` menu item.
1. On the left side of the screen find the `Captions` menu item.
1. Turn the trigger to `Off` to disable native captions display in the
   Video XBlock.

![disable captions in Wistia](doc/img/wistia_1.png)

### HTML 5

This provider is used to play videos uploaded to the Platform or located
elsewhere (the backend processes the direct URL to the video).
Currently, at the backend level, the option to use Default Timed Transcript
for HTML5 has been disabled through the exclusion of advanced fields:
`exclude_advanced_fields = ('default_transcripts', 'download_video_url')`
As a result, for the HTML5 provider, the fields for Default Timed Transcript
and Video API Token in the Advanced Settings (located below the Enabled
transcripts field) are disabled.

![disable Default Timed Transcript and Video API Token in HTML_5](doc/img/HTML_5.png)

#### Additional information on downloading default transcripts

When uploading a transcript file to the platform, check the format of the file.
The format of the uploaded transcript file must be *.vtt* or *.srt*.
During the loading to the Video Xblock - the .vtt files are fetched
directly without conversion. If the file format is *.srt*, then the file
is converted and saved on the platform in *.vtt* format.
If the file format is *.vtt*, upload it to the platform occurs without any changes.

### Kown issues

1. **YouTube** video hasn't been reproduced in Chrome:
    - doesnʼt work with Chrome on MacOS
    - works fine with Safari and Firefox on MacOS
    - if add a video block and default video to the same page - the video
    block works only after the default video was played
1. The operation of the **Brightcove** service has not been fully tested, due
to the need for a paid account.
1. The transcription-receiving functionality is only available for paid **Wistia** plans.
1. The **Vimeo** player will only display subtitles uploaded through the Vimeo
platform account web page. Transcripts uploaded through the Studio for the video
block can be used only for download.

### Set default values in config files

Now it is possible to indicate prepopulated values for any xblock field
per site installation (see note below).

Sample default settings in `/edx/app/edxapp/cms.env.json`:

```json
    "XBLOCK_SETTINGS": {
      "video_xblock": {
        "threeplaymedia_apikey": "987654321",
        "account_id": "1234567890"
      }
    }
```
Note: here above each provided key corresponds to SITE_NAME environment variable value.

### Allowed Handouts file types

+ __images:__ .gif, .ico, .jpg, .jpeg, .png, .tif, .tiff, .bmp, .svg,
+ __documents:__ .pdf, .txt, .rtf, .csv,
+ __MSOffice:__ .doc, .docx, .xls, .xlsx, .ppt, .pptx, .pub,
+ __openOffice:__ .odt, .ods, .odp,
+ __archives:__ .zip, .7z, .gzip, .tar,
+ __other:__ .html, .xml, .js, .sjson,
+ __transcripts:__ .srt, .vtt

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

## Translations

Run docker container to work with translations, tests etc.

```shell
> cd xblock-video
> docker run -it --rm --name video-xblock-tests -v $(pwd):/app seriallab/python3.5dev  bash
> cd app
> export VIRTUAL_ENV=$(pwd)
> apt-get install -y gettext
> make deps-test
```

To add new language for translation:

- add appropriate language to the translations.settings.LANGUAGE variable
- create `<lang>`/LC_MESSAGES/ directory and copy there the text.po file from english language
- run:

```shell
> make compile_translations
```


## License

The code in this repository is licensed under the GPL v3 licence unless
otherwise noted.

Please see `LICENSE` file for details.
