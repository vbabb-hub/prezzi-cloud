// Rigenerare docs/tailwind.css dopo ogni modifica alle classi di docs/index.html o docs/app.js:
//   npx tailwindcss@3.4.17 -c tailwind/tailwind.config.js -i tailwind/input.css -o docs/tailwind.css --minify
module.exports = { content: ["./docs/index.html", "./docs/app.js"], theme: { extend: {} }, plugins: [] };
