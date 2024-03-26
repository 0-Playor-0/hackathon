document.addEventListener('DOMContentLoaded', function() {
    const postImages = document.querySelectorAll('.post img');
    postImages.forEach(function(img) {
        img.addEventListener('load', function() {
            
            const maxWidth = 200;
            const maxHeight = 200;
            if (img.width > maxWidth || img.height > maxHeight) {
                if (img.width / maxWidth > img.height / maxHeight) {
                    img.width = maxWidth;
                    img.height *= (maxWidth / img.width);
                } else {
                    img.height = maxHeight;
                    img.width *= (maxHeight / img.height);
                }
            }
        });
    });
});