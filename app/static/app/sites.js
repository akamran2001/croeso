/**
 * All of the tags and titles visible on the page
 */
const data = {
  titles: [...document.querySelectorAll(".site-title")].map((title) =>
    title.textContent.trim().toLowerCase()
  ),
  tags: [...document.querySelectorAll(".tag-name")].map((tag) =>
    tag.textContent.trim().toLowerCase()
  ),
};

/**
 * Takes the inputed string in the searchbar and returns all titles and tags that contain the search term
 * @param {string} val Current input in searchbar
 * @returns {string[]} Array of suggested titles and tags
 */
const get_suggestions = (val) => {
  let titles = data.titles.filter((title) => {
    return title.includes(val);
  });

  let tags = data.tags
    .filter((tag) => {
      return tag.includes(val.slice(1)) && val.charAt(0) === "#";
    })
    .map((tag) => `#${tag}`);

  return Array.from(new Set([...titles, ...tags])).sort(); //Ensure suggestions are not repeated and sorted
};

/**
 * Highlight the hovered item on the search suggestions
 * @param {Event} e
 */
const search_hover = (e) => {
  if (e.type === "mouseover") {
    e.currentTarget.classList.add("active");
  }
  if (e.type === "mouseleave") {
    e.currentTarget.classList.remove("active");
  }
};

/**
 * When the user clicks on a search suggestion fill it in the search bar and reset the suggestions
 * @param {Event} e
 */
const selected = (e) => {
  const val = e.currentTarget.textContent;
  document.getElementById("search-suggestions").innerHTML = "";
  document.getElementById("search-input").value = val;
};

/**
 * Format the given search suggestion to be in title case (first letter of every word capitalized)
 * @param {string} s
 * @returns {string}
 */
const title_case = (s) => {
  return s
    .split(" ")
    .map((word) => `${word.charAt(0).toUpperCase()}${word.slice(1)}`)
    .join(" ");
};

/**
 * Populate a list of search suggestions as the user types on the search bar
 * @param {Event} e
 */
const searching = (e) => {
  const ul = document.getElementById("search-suggestions");
  const val = e.currentTarget.value.toLowerCase();
  ul.innerHTML = "";
  if (val !== null && val.trim() !== "") {
    get_suggestions(val).forEach((s) => {
      const li = document.createElement("li");
      li.appendChild(document.createTextNode(title_case(s)));
      li.classList.add("list-group-item", "suggested", "faded-out");
      li.addEventListener("mouseover", search_hover);
      li.addEventListener("mouseleave", search_hover);
      li.addEventListener("click", selected);
      ul.appendChild(li);
      requestAnimationFrame(() => {
        li.classList.remove("faded-out");
      });
    });
  }
};
