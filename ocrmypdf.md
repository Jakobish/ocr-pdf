usage: OCRmyPDF [-h] [-l LANGUAGES] [--image-dpi DPI]
                [--output-type {pdfa,pdf,pdfa-1,pdfa-2,pdfa-3,none}]
                [--sidecar [FILE]] [--version] [-j N] [-q] [-v [VERBOSE]]
                [--title TITLE] [--author AUTHOR] [--subject SUBJECT]
                [--keywords KEYWORDS] [-r] [--remove-background] [-d] [-c]
                [-i] [--unpaper-args UNPAPER_ARGS] [--oversample DPI]
                [--remove-vectors] [-f] [-s] [--redo-ocr] [--skip-big MPixels]
                [--invalidate-digital-signatures] [--pages PAGES]
                [--max-image-mpixels MPixels]
                [--pdf-renderer {auto,hocr,sandwich,hocrdebug}]
                [--rotate-pages-threshold CONFIDENCE]
                [--fast-web-view MEGABYTES] [--continue-on-soft-render-error]
                [--plugin PLUGINS] [-k] [--tesseract-config CFG]
                [--tesseract-pagesegmode PSM] [--tesseract-oem MODE]
                [--tesseract-thresholding METHOD]
                [--tesseract-timeout SECONDS]
                [--tesseract-non-ocr-timeout SECONDS]
                [--tesseract-downsample-large-images | --no-tesseract-downsample-large-images]
                [--tesseract-downsample-above TESSERACT_DOWNSAMPLE_ABOVE]
                [--user-words FILE] [--user-patterns FILE] [-O {0,1,2,3}]
                [--jpeg-quality Q] [--png-quality Q] [--jbig2-lossy]
                [--jbig2-threshold T] [--color-conversion-strategy STRATEGY]
                [--pdfa-image-compression {auto,jpeg,lossless}]
                input_pdf_or_image output_pdf

Generates a searchable PDF or PDF/A from a regular PDF.

OCRmyPDF rasterizes each page of the input PDF, optionally corrects page
rotation and performs image processing, runs the Tesseract OCR engine on the
image, and then creates a PDF from the OCR information.

positional arguments:
  input_pdf_or_image    PDF file containing the images to be OCRed (or '-' to
                        read from standard input)
  output_pdf            Output searchable PDF file (or '-' to write to
                        standard output). Existing files will be overwritten.
                        If same as input file, the input file will be updated
                        only if processing is successful.

options:
  -h, --help            show this help message and exit
  -l, --language LANGUAGES
                        Language(s) of the file to be OCRed (see tesseract
                        --list-langs for all language packs installed in your
                        system). Use -l eng+deu for multiple languages.
  --image-dpi DPI       When the input file is an image, not a PDF, use this
                        DPI instead of the DPI claimed by the input file. If
                        the input does not claim a sensible DPI, this option
                        will be required.
  --output-type {pdfa,pdf,pdfa-1,pdfa-2,pdfa-3,none}
                        Choose output type. 'pdfa' creates a PDF/A-2b
                        compliant file for long term archiving (default,
                        recommended) but may not suitable for users who want
                        their file altered as little as possible. 'pdfa' also
                        has problems with full Unicode text. 'pdf' minimizes
                        changes to the input file. 'pdf-a1' creates a PDF/A-1b
                        file. 'pdf-a2' is equivalent to 'pdfa'. 'pdf-a3'
                        creates a PDF/A-3b file. 'none' will produce no
                        output, which may be helpful if only the --sidecar is
                        desired.
  --sidecar [FILE]      Generate sidecar text files that contain the same text
                        recognized by Tesseract. This may be useful for
                        building a OCR text database. If FILE is omitted, the
                        sidecar file be named {output_file}.txt; the next
                        argument must NOT be the name of the input PDF. If
                        FILE is set to '-', the sidecar is written to stdout
                        (a convenient way to preview OCR quality). The output
                        file and sidecar may not both use stdout at the same
                        time.
  --version             Print program version and exit

Job control options:
  -j, --jobs N          Use up to N CPU cores simultaneously (default: use
                        all).
  -q, --quiet           Suppress INFO messages
  -v, --verbose [VERBOSE]
                        Print more verbose messages for each additional
                        verbose level. Use `-v 1` typically for much more
                        detailed logging. Higher numbers are probably only
                        useful in debugging.

Metadata options:
  Set output PDF/A metadata (default: copy input document's metadata)

  --title TITLE         Set document title (place multiple words in quotes)
  --author AUTHOR       Set document author
  --subject SUBJECT     Set document subject description
  --keywords KEYWORDS   Set document keywords

Image preprocessing options:
  Options to improve the quality of the final PDF and OCR

  -r, --rotate-pages    Automatically rotate pages based on detected text
                        orientation
  --remove-background   Attempt to remove background from gray or color pages,
                        setting it to white
  -d, --deskew          Deskew each page before performing OCR
  -c, --clean           Clean pages from scanning artifacts before performing
                        OCR, and send the cleaned page to OCR, but do not
                        include the cleaned page in the output
  -i, --clean-final     Clean page as above, and incorporate the cleaned image
                        in the final PDF. Might remove desired content.
  --unpaper-args UNPAPER_ARGS
                        A quoted string of arguments to pass to unpaper.
                        Requires --clean. Example: --unpaper-args '--layout
                        double'.
  --oversample DPI      Oversample images to at least the specified DPI, to
                        improve OCR results slightly
  --remove-vectors      EXPERIMENTAL. Mask out any vector objects in the PDF
                        so that they will not be included in OCR. This can
                        eliminate false characters.

OCR options:
  Control how OCR is applied

  -f, --force-ocr       Rasterize any text or vector objects on each page,
                        apply OCR, and save the rastered output (this rewrites
                        the PDF)
  -s, --skip-text       Skip OCR on any pages that already contain text, but
                        include the page in final output; useful for PDFs that
                        contain a mix of images, text pages, and/or previously
                        OCRed pages
  --redo-ocr            Attempt to detect and remove the hidden OCR layer from
                        files that were previously OCRed with OCRmyPDF or
                        another program. Apply OCR to text found in raster
                        images. Existing visible text objects will not be
                        changed. If there is no existing OCR, OCR will be
                        added.
  --skip-big MPixels    Skip OCR on pages larger than the specified amount of
                        megapixels, but include skipped pages in final output
  --invalidate-digital-signatures
                        Normally, OCRmyPDF will refuse to OCR a PDF that has a
                        digital signature. This option allows OCR to proceed,
                        but the digital signature will be invalidated.

Advanced:
  Advanced options to control OCRmyPDF

  --pages PAGES         Limit OCR to the specified pages (ranges or comma
                        separated), skipping others
  --max-image-mpixels MPixels
                        Set maximum number of megapixels to unpack before
                        treating an image as a decompression bomb
  --pdf-renderer {auto,hocr,sandwich,hocrdebug}
                        Choose OCR PDF renderer - the default option is to let
                        OCRmyPDF choose. See documentation for discussion.
  --rotate-pages-threshold CONFIDENCE
                        Only rotate pages when confidence is above this value
                        (arbitrary units reported by tesseract)
  --fast-web-view MEGABYTES
                        If the size of file is more than this threshold (in
                        MB), then linearize the PDF for fast web viewing. This
                        allows the PDF to be displayed before it is fully
                        downloaded in web browsers, but increases the space
                        required slightly. By default we skip this for small
                        files which do not benefit. If the threshold is 0 it
                        will be apply to all files. Set the threshold very
                        high to disable.
  --continue-on-soft-ocrender-error
                        Continue processing pages after a recoverable PDF
                        rendering error. A recoverable error is one that does
                        not prevent the page from being rendered, but may
                        result in visual differences compared to the input
                        file. Missing fonts are a typical source of these
                        errors.
  --plugin PLUGINS      Name of plugin to import. Argument may be issued
                        multiple times to import multiple plugins. Plugins may
                        be specified as module names in Python syntax,
                        provided they are installed in the same Python
                        (virtual) environment as ocrmypdf; or you may give the
                        path to the Python file that contains the plugin.
                        Plugins must conform to the specification in the
                        OCRmyPDF documentation.

Debugging:
  Arguments to help with troubleshooting and debugging

  -k, --keep-temporary-files
                        Keep temporary files (helpful for debugging)

Tesseract:
  Advanced control of Tesseract OCR

  --tesseract-config CFG
                        Additional Tesseract configuration files -- see
                        documentation.
  --tesseract-pagesegmode PSM
                        Set Tesseract page segmentation mode (see tesseract
                        --help).
  --tesseract-oem MODE  Set Tesseract 4+ OCR engine mode: 0 - original
                        Tesseract only; 1 - neural nets LSTM only; 2 -
                        Tesseract + LSTM; 3 - default.
  --tesseract-thresholding METHOD
                        Set Tesseract 5.0+ input image thresholding mode. This
                        may improve OCR results on low quality images or those
                        that contain high contrast color. legacy-otsu is the
                        Tesseract default; adaptive-otsu is an improved Otsu
                        algorithm with improved sort for background color
                        changes; sauvola is based on local standard deviation.
  --tesseract-timeout SECONDS
                        Give up on OCR after the timeout, but copy the
                        preprocessed page into the final output. This timeout
                        is only used when using Tesseract for OCR. When
                        Tesseract is used for other operations such as
                        deskewing and orientation, the timeout is controlled
                        by --tesseract-non-ocr-timeout.
  --tesseract-non-ocr-timeout SECONDS
                        Give up on non-OCR operations such as deskewing and
                        orientation after timeout. This is a separate timeout
                        from --tesseract-timeout because these operations are
                        not as expensive as OCR.
  --tesseract-downsample-large-images, --no-tesseract-downsample-large-images
                        Downsample large images before OCR. Tesseract has an
                        upper limit on the size images it will support. If
                        this argument is given, OCRmyPDF will downsample large
                        images to fit Tesseract. This may reduce OCR quality,
                        on large images the most desirable text is usually
                        larger. If this parameter is not supplied, Tesseract
                        will error out and produce no OCR on the page in
                        question. This argument should be used with a high
                        value of --tesseract-timeout to ensure Tesseract has
                        enough to time.
  --tesseract-downsample-above TESSERACT_DOWNSAMPLE_ABOVE
                        Downsample images larger than this size pixel size in
                        either dimension before OCR. --tesseract-downsample-
                        large-images downsamples only when an image exceeds
                        Tesseract's internal limits. This argument causes
                        downsampling to occur when an image exceeds the given
                        size. This may reduce OCR quality, but on large images
                        the most desirable text is usually larger.
  --user-words FILE     Specify the location of the Tesseract user words file.
                        This is a list of words Tesseract should consider
                        while performing OCR in addition to its standard
                        language dictionaries. This can improve OCR quality
                        especially for specialized and technical documents.
  --user-patterns FILE  Specify the location of the Tesseract user patterns
                        file.

Optimization options:
  Control how the PDF is optimized after OCR

  -O, --optimize {0,1,2,3}
                        Control how PDF is optimized after processing:0 - do
                        not optimize; 1 - do safe, lossless optimizations
                        (default); 2 - do lossy JPEG and JPEG2000
                        optimizations; 3 - do more aggressive lossy JPEG and
                        JPEG2000 optimizations. To enable lossy JBIG2, see
                        --jbig2-lossy.
  --jpeg-quality Q      Adjust JPEG quality level for JPEG optimization. 100
                        is best quality and largest output size; 1 is lowest
                        quality and smallest output; 0 uses the default.
  --png-quality Q       Adjust PNG quality level to use when quantizing PNGs.
                        Values have same meaning as with --jpeg-quality
  --jbig2-lossy         Enable JBIG2 lossy mode (better compression, not
                        suitable for some use cases - see documentation). Only
                        takes effect if --optimize 1 or higher is also
                        enabled.
  --jbig2-threshold T   Adjust JBIG2 symbol code classification threshold
                        (default 0.85), range 0.4 to 0.9.

Ghostscript:
  Advanced control of Ghostscript

  --color-conversion-strategy STRATEGY
                        Set Ghostscript color conversion strategy
  --pdfa-image-compression {auto,jpeg,lossless}
                        Specify how to compress images in the output PDF/A.
                        'auto' lets OCRmyPDF decide. 'jpeg' changes all
                        grayscale and color images to JPEG compression.
                        'lossless' uses PNG-style lossless compression for all
                        images. Monochrome images are always compressed using
                        a lossless codec. Compression settings are applied to
                        all pages, including those for which OCR was skipped.
                        Not supported for --output-type=pdf ; that setting
                        preserves the original compression of all images.

OCRmyPDF attempts to keep the output file at about the same size.  If a file
contains losslessly compressed images, and images in the output file will be
losslessly compressed as well.

PDF is a page description file that attempts to preserve a layout exactly.
A PDF can contain vector objects (such as text or lines) and raster objects
(images).  A page might have multiple images.  OCRmyPDF is prepared to deal
with the wide variety of PDFs that exist in the wild.

When a PDF page contains text, OCRmyPDF assumes that the page has already
been OCRed or is a "born digital" page that should not be OCRed.  The default
behavior is to exit in this case without producing a file.  You can use the
option --skip-text to ignore pages with text, or --force-ocr to rasterize
all objects on the page and produce an image-only PDF as output.

    ocrmypdf --skip-text file_with_some_text_pages.pdf output.pdf

    ocrmypdf --force-ocr word_document.pdf output.pdf

If you are concerned about long-term archiving of PDFs, use the default option
--output-type pdfa which converts the PDF to a standardized PDF/A-2b.  This
removes some features from the PDF such as Javascript or forms. If you want to
minimize the number of changes made to your PDF, use --output-type pdf.

If OCRmyPDF is given an image file as input, it will attempt to convert the
image to a PDF before processing.  For more control over the conversion of
images to PDF, use the Python package img2pdf or other image to PDF software.

For example, this command uses img2pdf to convert all .png files beginning
with the 'page' prefix to a PDF, fitting each image on A4-sized paper, and
sending the result to OCRmyPDF through a pipe.

    img2pdf --pagesize A4 page*.png | ocrmypdf - myfile.pdf

Online documentation is located at:
    https://ocrmypdf.readthedocs.io/en/latest/introduction.html
