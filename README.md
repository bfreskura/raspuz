# Projekt iz raspoznavanja uzoraka

## Installation
1. Install all python (pip) packages from the `requirements.txt` file

## How to acquire images
Run `python2 imag_aq.py [-options]`.
To see available options run: `python2 imag_aq.py -h`

## Configurable Parameters
* Exposure
* Gamma
* BalanceWhiteAuto = Continuous
* BlackLevel
* EdgeFilter = Sharpen1

### Exposure
* Option name: ExposureTimeAbs [Float]

* **DESCRIPTION**:
Exposure duration, in microseconds.

* **FEATURE NAME**: ExposureTimeAbs
* **VISIBILITY**: BEGINNER
* **TYPE**: Float
* **MINIMUM**: 26
* **MAXIMUM**: 60000000
* **CATEGORY**: /Controls/Exposure

* **AFFECTED FEATURE(S)**:
AcquisitionFrameRateAbs, AcquisitionFrameRateLimit

### Gamma
* Option Name: Gamma [Float]

* **DESCRIPTION**:
Applies gamma value to the raw sensor signal (via LUT).

* **FEATURE NAME**: Gamma

* **VISIBILITY**: BEGINNER

* **TYPE**: Float

* **MINIMUM**: 0.449999988079071

* **MAXIMUM**: 1

* **CATEGORY**: /Controls

* **AFFECTED FEATURE(S)**: N/A

### BlackLevel
* Option Name: BlackLevel

* **DESCRIPTION**:
Black level (offset) value.

* **FEATURE NAME**: BlackLevel

* **VISIBILITY**: BEGINNER

* **TYPE**: Float

* **MINIMUM**: 0

* **MAXIMUM**: 255.75
* **CATEGORY**: /Controls/BlackLevelControl

* **AFFECTED FEATURE(S)**: N/A

## Troubleshooting
### Images are half empty and the error occurs if the camera tries to capture multiple images
Just increase the `frame_wait` parameter in the `capture_image` method.
