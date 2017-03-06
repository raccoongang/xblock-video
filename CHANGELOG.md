# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]
### Added
- Html5 video support.
- UI improvements in Studio:
    - Split Video XBlock settings into Basic & Advanced tabs.
    - Display only fields relevant to selected video
- Manual uploaded transcripts validation: file extension and size.

### Fixed
- Various bugs.
- Code stabilization.

## [v0.4.0] - 2017-02-07

### Added
- Brightcove content protection and auto-quality
    - On API authentication uploads two custom Ingest Profiles:
        - Creates new API credentials with required permissions
        - HLS for auto quality
        - HLSe for auto qualify & encryption

- Add new UI controls after a user has authenticated against Brightcove API:
    - View video tech info
    - Send video re-transcode request on a Brightcove side

- Default transcripts upload
    - Allows to fetch transcripts from the platform and store them into XBlock.
    - Supports: Brightcove, Youtube & Wistia.
    - Brightcove & Wistia require API authentication before default transcripts upload can work.

### Fixed
- Various bugfixes and improvements.
