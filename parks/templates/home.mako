<%inherit file="base.mako"/>
<%block name="content">
    <div id="park-carousel" class="carousel slide" style="width: 640px; margin-left: auto; margin-right: auto;">
        <div class="carousel-inner">
            <div class="active item">
                <img src="${carousel_image_urls_captions[0].url}">
                <div class="carousel-caption">
                    <h4>${carousel_image_urls_captions[0].caption_header}</h4>
                    <p>${carousel_image_urls_captions[0].caption}</p>
                </div>
            </div>
            % for url, caption_header, caption in carousel_image_urls_captions[1:]:
                <div class="item">
                    <img src="${url}">
                    <div class="carousel-caption">
                        <h4>${caption_header}</h4>
                        <p>${caption}</p>
                    </div>
                </div>
            % endfor
        </div>
        <a class="carousel-control left" href="#park-carousel" data-slide="prev">&lsaquo;</a>
        <a class="carousel-control right" href="#park-carousel" data-slide="next">&rsaquo;</a>
    </div>
</%block>
