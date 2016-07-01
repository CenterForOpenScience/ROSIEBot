<?php
// Allowed mirrors:
$officials = array("http://localhost:8888/",);

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
            }
            .io {
            min-width: 20px;
            min-height: 10px;
            display: inline;
            padding: 5px;
            color: white;
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
        </style>
    </head>
    <body>
        <h2>
            Verify Authenticity by
            <?php echo $_SERVER['SERVER_NAME']; ?>
        </h2>
        <div>
            Authenticity for
            <?php
            echo $ref . ' ';

            if (array_search($ref, $officials) !== false) {

                echo '<div class="io passed">Passed</div>';
                echo '<h3> Is <div class="io mirror">' . $displayref . '</div> the site you navigated to?</h3>';

                echo "<h2> Do not trust this site if it isn't " . $displayref . ". </h2>";
            }

            else {

                echo '<div class="io failed">Failed</div>';
                echo "<h2> Do not trust this site. </h2>";
            }
            ?>
        </div>
    </body>
</html>