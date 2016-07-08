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
            font-family: Helvetica Neue;
            padding: 50px;
            background: linear-gradient(#C5D6E6, white);
            }
            header {
            background-color: #214762;
            position: relative;
            top: 0;
            color: white;
            width: 100%;
            left: 0;
            padding-left: 17%;
            padding-top: 5px;
            margin: -10px;
            }
            header img {
            margin: 20px;
            }
            .contain {
            position: relative;
            top: 60px;
            background-color: rgba(255,255,255,.49);
            border-radius: 5px;
            padding: 10px;
            margin:auto;
            margin-top: 20px;
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
        <header>
            <img style="float: left;" src="/static/img/cos-white2.png" class="osf-navbar-logo" width="27" alt="COS logo">
            <p style="font-size: 20px;"> OSF Mirror Authentication </p>
        </header>

        <div class="contain">
            <p class="row"> <em> Referring URL: </em> <a href='<?php echo $displayref; ?>'> <?php echo $displayref; ?> </a>
            <p class="row">
            <?php
            $officials = array("http://localhost:8888/", "http://127.0.0.1:6565/approved_mirror.html", "http://localhost:6565/approved_mirror.html");

            if (array_search($ref, $officials) !== false) {

                echo '<em> Mirror integrity: </em><span class="io passed"> Passed </span></p>';
                echo '<h3 class="row"> Is <span class="io mirror">' . $displayref . '</span> the site you navigated to?</h3>';
                echo "</div>
                      <div class='contain'>
                          <h2 class='row'><a href='" . $displayref . "'> " . $displayref . "</a> is trustworthy.</h2><h3 class='row'> Verify this is the site that brought you here.</h3>
                      </div>";
            }

            else {

                echo '<em> Mirror integrity: </em> <span class="io failed"> Unknown </span></p>';
                echo "</div>
                      <div class='contain'>
                        <h2 class='row'> This site may not be a faithful mirror of the OSF. </h2>
                      </div>";
            }
            ?>
        </div>
        <footer class="row">
            Maintained by the <a href="//cos.io"> Center for Open Science </a>
        </footer>
    </body>
</html>
