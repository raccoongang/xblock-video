# xblock-video
XBlock to embed videos hosted on different video platform into your courses.

## Installation

```bash
sudo -sHu edxapp
source ~/edxapp_env
pip install xblock-utils==1.0.2
pip install -e "git+https://github.com/raccoongang/xblock-video.git@767821d63aba3b4f9e2630120e3d480857b8cea3#egg=xblock-video==0.1"
cd video_xblock/static
bower install
```

## Enabling in Studio
You can enable the Wistia xblock in studio through the advanced
settings:

1. From the main page of a specific course, click on *Settings*,
   *Advanced Settings* in the top menu.
1. Check for the *Advanced Module List* policy key, and add
   `"video_xblock"` in the policy value list.
   ![Advanced Module List](https://placehold.it/350x150?text=Here+be+Screenshot)

1. Click on the *Save changes* button.

## Usage

TODO

## License

The code in this repository is licensed under the GPL v3 licence unless otherwise noted.

Please see `LICENSE` file for details.
