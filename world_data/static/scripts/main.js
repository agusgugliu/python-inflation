function toggleImages() {
  const img1 = document.getElementById("img1");
  const img2 = document.getElementById("img2");

  if (img1.classList.contains("hidden")) {
    img1.classList.remove("hidden");
    img2.classList.add("hidden");
  } else {
    img1.classList.add("hidden");
    img2.classList.remove("hidden");
  }
}
