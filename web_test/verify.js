const verifyTerms = () => {
    console.log("verified");
};

data = [
    {
      swe: "test",
      eng: "test",
      swe_inf: "testböj",
      eng_inf: "testinfl",
      pos: "N",
      at: "teast",
      src: "emelie"
    },
    {
      swe: "test2",
      eng: "test2",
      swe_inf: "testböj2",
      eng_inf: "testinfl2",
      pos: "N2",
      at: "teast2",
      src: "emelie2"
    },
    {
      swe: "test3",
      eng: "test3",
      swe_inf: "testböj3",
      eng_inf: "testinfl3",
      pos: "N3",
      at: "teast3",
      src: "emelie3"
    },
    {
      swe: "test4",
      eng: "test4",
      swe_inf: "testböj4",
      eng_inf: "testinfl4",
      pos: "N4",
      at: "teast4",
      src: "emelie4"
    },
    {
      swe: "test5",
      eng: "test5",
      swe_inf: "testböj5",
      eng_inf: "testinfl5",
      pos: "N5",
      at: "teast5",
      src: "emelie5"
    }
]  

window.onload = function() {
    generateCheckboxes(data);
};

function generateCheckboxes(data) {
    const container = document.getElementById('term-verification');
    data.forEach((row, index) => {
        // Create a div for each checkbox
        const checkboxContainer = document.createElement('div');
        checkboxContainer.className = 'checkbox-container';

        // Create the checkbox
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `term${index}`;
        checkbox.name = `term${index}`;
        checkbox.value = row.swe;
        checkbox.checked = true;

        // Create the label
        const label = document.createElement('label');
        label.htmlFor = `term${index}`;
        label.textContent = `${row.swe}, ${row.eng}, ${row.swe_inf}, ${row.eng_inf}, ${row.pos}, ${row.at}, ${row.src}`;

        // Append the checkbox and label to the container
        checkboxContainer.appendChild(checkbox);
        checkboxContainer.appendChild(label);

        // Append the container to the main container
        container.appendChild(checkboxContainer);
    });
}
