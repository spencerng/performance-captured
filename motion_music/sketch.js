//Code derived from https://kylemcdonald.github.io/cv-examples/
// https://inspirit.github.io/jsfeat/sample_canny_edge.html

var capture;
var buffer;
var result;
var aspect = 3/2;
var screenScale = 0.5;
var h = 1080 * screenScale;
var w = aspect * h;
var flow;
var prevBuffers = []
var MAX_BUFFER = 10;

var r = 0;
var g = 0;
var b = 0;

var peakDetect, fft;



function setup() {
    capture = createCapture({
        audio: false,
        video: {
            width: w,
            height: h
        }
    }, function() {
        console.log('capture ready.')
    });
    capture.elt.setAttribute('playsinline', '');
    createCanvas(w, h);
    capture.size(w, h);
    capture.hide();
    flow = new FlowCalculator(100);
    buffer = new jsfeat.matrix_t(w, h, jsfeat.U8C1_t);

    fft = new p5.FFT();
    peakDetect = new p5.PeakDetect();
    fullscreen(true);
}

// Clap = background change to random color
// See motion trace of the past
// Music = speed up/down based 


function jsfeatToP5(src, dst, layerNum) {
    if (layerNum == 0 || !dst || dst.width != src.cols || dst.height != src.rows) {
        dst = createImage(src.cols, src.rows);
    }
    dst.loadPixels();
    var srcData = src.data;
    var dstData = dst.pixels;
    for (var i = 0, j = 0; i < src.data.length; i++) {
        var cur = srcData[i];
        console.log(cur)
        if (cur == 0) {
            if (layerNum == 0) {
                dstData[j++] = 0;
                dstData[j++] = 0;
                dstData[j++] = 0;
                dstData[j++] = 255;
            } else {
                j += 4;
            }
        } else {
            dstData[j++] = r * layerNum / MAX_BUFFER;
            dstData[j++] = g * layerNum / MAX_BUFFER;
            dstData[j++] = b * layerNum / MAX_BUFFER;
            dstData[j++] = 255;
        }
    }
    dst.updatePixels();
    return dst;
}

function draw() {
    clear()
    //fft.analyze();
    //peakDetect.update(fft);

    if (peakDetect.isDetected) {
        r = random(0, 256);
        g = random(0, 256);
        b = random(0, 256);
    }


    capture.loadPixels();
    if (capture.pixels.length <= 0) {
        return
    }

    var blurSize = 50;
    var lowThreshold = 20;
    var highThreshold = 50;

    blurSize = map(blurSize, 0, 100, 1, 12);
    lowThreshold = map(lowThreshold, 0, 100, 0, 255);
    highThreshold = map(highThreshold, 0, 100, 0, 255);

    jsfeat.imgproc.grayscale(capture.pixels, w, h, buffer);
    jsfeat.imgproc.gaussian_blur(buffer, buffer, blurSize, 0);
    jsfeat.imgproc.canny(buffer, buffer, lowThreshold, highThreshold);

    var n = buffer.rows * buffer.cols;

    prevBuffers.push(buffer);
    if (prevBuffers.length > MAX_BUFFER) {
        prevBuffers.shift();
    }
    
    for (var i = 0; i < prevBuffers.length; i++) {
        result = jsfeatToP5(prevBuffers[i], result, i);
    }
    
    
    image(result, 0, 0, w, h);


}
