const handleData = ($component) => {
  if ($component.innerHTML !== "") {
    const val = $component.innerHTML;
    const [info, json] = val.split(";");

    if (json != null) {
      const image_data = JSON.parse(json);

      image_data.forEach((_data) => {
        addImageScore(_data);
      });

      $component.innerHTML = info; // we don't have the score data
    }
  }
};

// Need to query for all images in the gallery and get their seed
// if possible.  The seed should be the image identifier.
const addImageScore = (data) => {
  const $galleryImages = gradioApp().querySelectorAll(
    "#txt2img_gallery .gallery-item"
  );

  $galleryImages.forEach((img) => {
    const $div = document.createElement("div");
    $div.classList.add("caption");
    $div.innerHTML = `Score: ${data.score}`;

    img.appendChild($div);
  });
};

onUiUpdate(() => {
  const $htmlOutput = gradioApp().querySelector(
    "#txt2img_output_info p:not(.time)"
  );
  if ($htmlOutput) {
    handleData($htmlOutput);
  }
});
