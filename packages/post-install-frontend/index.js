const express = require("express");
const app = express();

const PORT = process.env.PORT || 3000;
const URL = process.env.URL || "https://raw.githubusercontent.com/urbanspr1nter/avg-dev/master/tools/scripts/post-install.sh";

app.get("/", function(req, res) {
    return res.send(`wget -qO- ${URL} | bash`);
});

app.listen(PORT, function() {
    console.log(`Server is listening on: ${PORT}`);
});

