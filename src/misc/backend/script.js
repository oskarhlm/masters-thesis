document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('uploadForm');
  const fileList = document.getElementById('fileList');

  form.addEventListener('submit', function(event) {
    event.preventDefault();
    const files = document.querySelector('input[type=file]').files;
    fileList.innerHTML = '';
    Array.from(files).forEach(function(file) {
      const reader = new FileReader();
      reader.onload = function() {
        const fileName = file.name;
        const listItem = document.createElement('li');
        listItem.textContent = fileName;
        fileList.appendChild(listItem);
      };
      reader.readAsDataURL(file);
    });
  });
});
