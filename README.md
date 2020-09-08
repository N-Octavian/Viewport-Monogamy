# Viewport Monogamy
# This add-on is for Blender users who have multiple GPUs. Currently, Cycles doesn't allow you to choose different devices for viewport rendering and final rendering, which is a bit of a bummer, since viewport rendering is not faster if you have multiple devices in use. From my testing, the viewport performance is roughly determined by the slowest device (if you have a GTX 1070 and a GTX 1060 selected for use, your viewport rendering performance will be closer to only having a GTX 1060 selected). This is not true for final rendering, where using multiple GPUs will give you a big boost in performance.
# Viewport Monogamy lets you select a device (a single device, I would recommend) for viewport rendering, and other devices for final rendering.
# Here is a video showing how it works:
# https://youtu.be/rIddu96tDYE
