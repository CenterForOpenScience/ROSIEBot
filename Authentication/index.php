<?php
if (isset($_SERVER['HTTP_REFERER'])) {
    $ref = $_SERVER['HTTP_REFERER'];
    $displayref = trim(trim($ref, 'http://'), 'https://');
} else {
    $ref = "None";
    $displayref = "N/A";
}
?>
<html>
    <head>
        <title> Mirror Verification </title>
        <style>
            body {
            font-family: Helvetica;
            padding: 50px;
            background: linear-gradient(#C5D6E6, white);
            }
            div {
            background-color: rgba(255,255,255,.49);
            border-radius: 5px;
            padding: 10px;
            margin:auto;
            width: 50%;
            }
            .row {
            border-radius: 3px;
            background-color: white;
            margin: 10px;
            padding: 10px;
            }
            .io {
            min-width: 20px;
            min-height: 10px;
            display: inline;
            padding: 5px;
            color: white;
            border-radius: 3px;
            }
            .mirror {
            background-color: yellow;
            color: black;
            }
            .passed {
            background-color: green;
            }
            .failed {
            background-color: red;
            }
            footer {
            position: absolute;
            bottom: 0px;
            }
        </style>
    </head>
    <body>
        <h2> OSF Mirror Authenticator </h2>
        <div>
            <p class="row">
            Authenticity for
            <?php
            echo $ref . ': ';
            $officials = array("http://localhost:8888/", "http://127.0.0.1:6565/approved_mirror.html", "http://localhost:6565/approved_mirror.html");

            if (array_search($ref, $officials) !== false) {

                echo '<span class="io passed">Passed</span></p>';
                echo '<h3 class="row"> Is <span class="io mirror">' . $displayref . '</span> the site you navigated to?</h3>';
                echo "<h2 class='row'> Do not trust this site if it isn't " . $displayref . ". </h2>";
            }

            else {

                echo '<span class="io failed">Failed</span></p>';
                echo "<h2 class='row'> Do not trust this site. </h2></div>";
            }
            ?>
        </div>
        <footer class="row">
            Maintained by the <a href="//cos.io"> Center for Open Science </a>
        </footer>
    </body>
</html>