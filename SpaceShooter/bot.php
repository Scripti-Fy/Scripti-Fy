<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');
$configFile = "config.json";

const hitam  = "\033[0;30m";
const merah  = "\033[0;31m";
const hijau  = "\033[0;32m";
const kuning = "\033[0;33m";
const biru   = "\033[0;34m";
const cyan   = "\033[0;36m";
const putih  = "\033[0;37m";
const reset  = "\033[0m";
const bg_hitam  = "\033[40m";
const bg_merah  = "\033[41m";
const bg_hijau  = "\033[42m";
const bg_kuning = "\033[43m";
const bg_biru   = "\033[44m";
const bg_ungu   = "\033[45m";
const bg_cyan   = "\033[46m";
const bg_putih  = "\033[47m";

const version     = "1.0";
const script_name = "spaceshooter.net";
const host        = "https://spaceshooter.net";
const in      = "https://api.waryono.my.id/in.php";

function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function uf() {
    return md5(uniqid(mt_rand(), true));
}

function zone() {
    return date_default_timezone_get();
}

function skibidixxx($url, $method = 'GET', $data = [], $headers = []) {
    while (true) {
        $ch = curl_init();
        $final_headers = [];
        foreach ($headers as $header) {
            $final_headers[] = $header;
        }
        $options = [
            CURLOPT_URL            => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HEADER         => true,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_SSL_VERIFYHOST => 1,
            CURLOPT_SSL_VERIFYPEER => true,
            CURLOPT_HTTPHEADER     => $final_headers,
            CURLOPT_CONNECTTIMEOUT => 999,
            CURLOPT_TIMEOUT        => 999
        ];
        if (strtoupper($method) === 'POST') {
            $options[CURLOPT_POST] = true;
            $options[CURLOPT_POSTFIELDS] = $data;
        }
        curl_setopt_array($ch, $options);
        $response = curl_exec($ch);
        if ($response) {
            $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
            $body = substr($response, $header_size);
            curl_close($ch);
            return $body;
        } else {
            curl_close($ch);
            echo "\33[1;" . rand(30, 37) . "mwiwok detok";
            sleep(1);
            echo "\r \r";
            return "ngelek";
        }
    }
}

function timer($seconds, $prefix = "[!] please wait") {
    $wait_time = (int)$seconds;
    $frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'];
    $frame_count = count($frames);
    $current_frame = 0;
    $frame_delay = 0.1;
    while ($wait_time > 0) {
        $start_time = microtime(true);
        while ((microtime(true) - $start_time) < 1) {
            $hours = floor($wait_time / 3600);
            $minutes = floor(($wait_time % 3600) / 60);
            $seconds_left = $wait_time % 60;
            $time_formatted = sprintf('%02d:%02d:%02d', $hours, $minutes, $seconds_left);
            $spinner = $frames[$current_frame];
            echo putih . $prefix . hijau . " $time_formatted " . putih . $spinner . "\r";
            usleep($frame_delay * 1000000);
            $current_frame = ($current_frame + 1) % $frame_count;
            if ((microtime(true) - $start_time) >= 1) break;
        }
        $wait_time--;
    }
    echo "\r                                     \r";
}

function rscaptcha($base64, $apikey) {
    $headers = ["Content-Type: application/json"];
    $body = json_encode([
        "apikey" => $apikey,
        "methods" => "upsidedown_2",
        "image" => $base64,
        "json" => 1
    ]);
    $request = skibidixxx(in, "POST", $body, $headers);
    if (strpos($request, "ERROR_WRONG_METHOD") !== false) { echo putih."Error: ".merah."ERROR_WRONG_METHOD\n"; exit; }
    if (strpos($request, "ERROR_KEY_DOES_NOT_EXIST") !== false) { echo putih."Error: ".merah."ERROR_KEY_DOES_NOT_EXIST\n"; exit; }
    if (strpos($request, "ERROR_METHOD_NOT_SPECIFIED") !== false) { echo putih."Error: ".merah."ERROR_METHOD_NOT_SPECIFIED\n"; exit; }
    if (strpos($request, "ERROR_NO_SUCH_METHOD") !== false) { echo putih."Error: ".merah."ERROR_NO_SUCH_METHOD\n"; exit; }
    if (strpos($request, "ERROR_DATABASE_CONNECTION_FAILED") !== false) { echo putih."Error: ".merah."ERROR_DATABASE_CONNECTION_FAILED\n"; exit; }
    if (strpos($request, "ERROR_TOO_MANY_REQUESTS") !== false) { echo putih."Error: ".merah."ERROR_TOO_MANY_REQUESTS"; sleep(1.8); echo "\r                                               \r"; return "ERROR_TOO_MANY_REQUESTS"; }
    if (strpos($request, "ERROR_WRONG_USER_KEY") !== false) { echo putih."Error: ".merah."ERROR_WRONG_USER_KEY\n"; exit; }
    if (strpos($request, "ERROR_ZERO_BALANCE") !== false) { echo putih."Error: ".merah."ERROR_ZERO_BALANCE\n"; exit; }
    if (strpos($request, "ERROR_BAD_PARAMETERS") !== false) { echo putih."Error: ".merah."ERROR_BAD_PARAMETERS\n"; exit; }
    if (strpos($request, "ERROR_EMPTY_IMAGE") !== false) { echo putih."Error: ".merah."ERROR_EMPTY_IMAGE\n"; exit; }
    if (strpos($request, "ERROR_UNKNOWN") !== false) { echo putih."Error: ".merah."ERROR_UNKNOWN\n"; exit; }
    $json = json_decode($request, true);
    $id = $json["request"];
    reload:
    timer(2);
    $url = "https://api.waryono.my.id/res.php?apikey=".$apikey."&action=get&id=".$id."&json=1";
    $result = skibidixxx($url, "GET", []);
    if (strpos($result, "ERROR_BAD_PARAMETERS") !== false) { echo putih."Error: ".merah."ERROR_BAD_PARAMETERS\n"; exit; }
    if (strpos($result, "Database connection failed") !== false) { echo putih."Error: ".merah."Database connection failed\n"; exit; }
    if (strpos($result, "WRONG_CAPTCHA_ID") !== false) { echo putih."Error: ".merah."WRONG_CAPTCHA_ID"; sleep(1.8); echo "\r                                               \r"; return "WRONG_CAPTCHA_ID"; }
    if (strpos($result, "ERROR_SOLVE_PENDING") !== false) { echo putih."Error: ".merah."ERROR_SOLVE_PENDING"; sleep(1.8); echo "\r                                               \r"; return "ERROR_SOLVE_PENDING"; }
    if (strpos($result, "CAPCHA_NOT_READY") !== false) { echo putih."Error: ".merah."CAPCHA_NOT_READY"; sleep(1.8); echo "\r                                               \r"; goto reload; }
    if (strpos($result, "ERROR_CAPTCHA_UNSOLVABLE") !== false) { echo putih."Error: ".merah."ERROR_CAPTCHA_UNSOLVABLE"; sleep(1.8); echo "\r                                               \r"; return "ERROR_CAPTCHA_UNSOLVABLE"; }
    if (strpos($result, "ERROR_BAD_REQUEST") !== false) { echo "Error: ".merah."ERROR_BAD_REQUEST\n"; exit; }
    if (strpos($result, "INTENAL_SERVER_ERROR") !== false) { echo "Errro: ".merah."INTENAL_SERVER_ERROR"; sleep(1.8); echo "\r                                               \r"; return "INTENAL_SERVER_ERROR"; }
    $json = json_decode($result, true);
    $res = $json["request"];
    preg_match('/x: (\d+), y: (\d+)/', $res, $match);
    return ["x" => $match[1], "y" => $match[2]];
}

function bypassCloudflare(&$config, $configFile, $target) {
    echo putih . "Cloudflare! wait.. ";
    $python_cmd = "python exec.py " . $target ." 2>/dev/null";
    $output = exec($python_cmd);
    $data_bypass = json_decode($output, true);
    if (isset($data_bypass['cf_clearance']) && !empty($data_bypass['cf_clearance'])) {
        $full_new_cf = $data_bypass['cf_clearance'];
        $new_ua = $data_bypass['user_agent'];
        $old_cookie = $config['cookie'];
        if (strpos($full_new_cf, '=') !== false) {
            $new_token_value = explode('=', $full_new_cf)[1];
        } else {
            $new_token_value = $full_new_cf;
        }
        $pattern = '/cf_clearance=[^;]+/';
        $replacement = "cf_clearance=" . $new_token_value;
        if (preg_match($pattern, $old_cookie)) {
            $new_cookie_str = preg_replace($pattern, $replacement, $old_cookie);
        } else {
            $new_cookie_str = rtrim($old_cookie, "; ") . "; " . $replacement;
        }
        $config['cookie'] = $new_cookie_str;
        $config['user_agent'] = $new_ua;
        file_put_contents($configFile, json_encode($config, JSON_PRETTY_PRINT));
        echo hijau . "Success Solver Cloudflare! WAF\n";
        echo putih."------------------------------------------------------\n";
        sleep(2);
        return true;
    } else {
        echo merah . "Error Bypass\n";
        echo putih."------------------------------------------------------\n";
        return false;
    }
}

function rspayload($html, $x, $y) {
    if (empty($html)) return false;
    $url = "https://api.waryono.my.id/rspayload.php";
    $headers = ["Content-Type: application/json"];
    $data = json_encode(["htmlContent" => $html, "clickX" => (int)$x, "clickY" => (int)$y]);
    $response = skibidixxx($url, "POST", $data, $headers);
    $resJson = json_decode($response, true);
    if (isset($resJson['Payload'])) {
        return ["fingerprint" => $resJson['Payload']];
    }
    return false;
}

function getConfig($configFile) {
    if (!file_exists($configFile)) {
        echo putih . "API Key: " . kuning;
        $apikey = trim(fgets(STDIN));
        echo putih . "Cookie: " . kuning;
        $coki = trim(fgets(STDIN));
        $data = ["apikey" => $apikey, "cookie" => $coki];
        file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
        echo hijau . "disimpan ke $configFile\n\n" . reset;
        sleep(3);
        return $data;
    }
    return json_decode(file_get_contents($configFile), true);
}

function banner() {
    echo putih  . "-----------------------------------------------------\n";
    echo putih  . "Script -> ".cyan.script_name.putih." Captcha ( RsCaptcha )\n";
    echo putih  . "Install Apk Seledroid Chromium and:\n";
    echo putih  . "1. pkg install php\n";
    echo putih  . "2. pkg install python\n";
    echo putih  . "3. pip install seledroid\n";
    echo putih  . "-----------------------------------------------------\n\n";
}

login:
clear();
banner();

$config = getConfig($configFile);
$apikey = $config['apikey'];
$coki   = $config['cookie'];
$ua     = $config['user_agent'] ?? "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36";

dash:
clear();
banner();

$a = [
    "host: ".script_name,
    "user-agent: " . $ua,
    "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
    "referer: ".host."/faucet/pepe",
    "cookie: " . $coki
];

$url = host."/dashboard";
$dash = skibidixxx($url, "GET", [], $a);

if ($dash == "ngelek" || strpos($dash, "Just a moment") !== false) {
    bypassCloudflare($config, $configFile, $url);
    $coki = $config['cookie'];
    $ua   = $config['user_agent'];
    goto dash;
}

if (strpos($dash, "Dashboard | SpaceShooter") !== false) {
    preg_match_all('/<a href="https:\/\/spaceshooter\.net\/faucet\/([^"]+)" class="">/', $dash, $matches);
    $currencies = $matches[1];
    usort($currencies, function($a, $b) {
        return strlen($a) - strlen($b);
    });
    $columns = 4;
    $total = count($currencies);
    for ($i = 0; $i < $total; $i++) {
        $num = $i + 1;
        $currency = strtoupper($currencies[$i]);
        echo putih."(" . str_pad($num, 2, ' ', STR_PAD_LEFT) . ") ".hijau . str_pad($currency, 6, ' ') . "".putih;
        if (($i + 1) % $columns == 0 || $i == $total - 1) {
            echo "\n";
        }
    }
    echo putih."chosee: ".merah;
    $handle = fopen("php://stdin", "r");
    $input = trim(fgets($handle));
    fclose($handle);
    if (!is_numeric($input)) {
        echo putih."Invalid input! Please enter a number.\n";
        sleep(2);
        goto dash;
    }
    $input = (int)$input;
    if ($input < 1 || $input > count($currencies)) {
        echo putih."Invalid selection! Please choose between 1-" . count($currencies) . "\n";
        sleep(4);
        goto dash;
    }
    $selectedCurrency = $currencies[$input-1];
    $memek = strtolower($selectedCurrency);
    echo putih."chosee: ".hijau .$memek. "\n\n";

    reload:
    while(true){
        $a = [
            "host: ".script_name,
            "user-agent: " . $ua,
            "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
            "referer: ".host."/dashboard",
            "cookie: " . $coki
        ];
        $b = [
            "host: rscaptcha.com",
            "user-agent: " . $ua,
            "accept: image/avif,image/webp,image/apng,image/svg+xml,image,q=0.8",
            "referer: ".host."/",
            "accept-language: id,en-US;q=0.9,en;q=0.8,ms;q=0.7,ru;q=0.6",
            "priority: i"
        ];
        $c = [
            "host: ".script_name,
            "origin: ".host,
            "content-type: application/x-www-form-urlencoded",
            "user-agent: " . $ua,
            "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
            "referer: ".host."/faucet/".$memek,
            "cookie: " . $coki
        ];

        $url = host."/faucet/".$memek;
        $faucet = skibidixxx($url, "GET", [], $a);

        if ($faucet == "ngelek" || strpos($faucet, "Just a moment") !== false) {
            bypassCloudflare($config, $configFile, $url);
            $coki = $config['cookie'];
            $ua   = $config['user_agent'];
            goto reload;
        }

        if (strpos($faucet, "Shortlinks | SpaceShooter") !== false) {
   	        echo putih."------------------------------------------------------\n";
            echo kuning."You Need to Complete Atleast 1 Shortlinks!\n";
            echo putih."enter to reload..";
            trim(fgets(STDIN));
            goto reload;
        }
        $rs_token = explode('"', explode('<input type="hidden" name="rscaptcha_token" value="', $faucet)[1])[0];
        $token = explode('"', explode('<input type="hidden" name="token" value="', $faucet)[1])[0];
        $rsimage = explode('"', explode('<img class="captcha-image" id="rscaptcha_img" src="', $faucet)[1])[0];

        $rsdownload = base64_encode(skibidixxx($rsimage, "GET", [], $b));
        $bypass = rscaptcha($rsdownload, $apikey);
        
        if (is_array($bypass)) {
            $x = $bypass["x"];
            $y = $bypass["y"];
        } elseif (in_array($bypass, ["WRONG_CAPTCHA_ID", "ERROR_CAPTCHA_UNSOLVABLE", "ERROR_TOO_MANY_REQUESTS", "ERROR_SOLVE_PENDING", "INTENAL_SERVER_ERROR"])) {
            goto reload;
        } else {
            echo putih . "Error: " . merah . " Tidak di ketahui!! coba lagi...\n";
            goto reload;
        }

        $payload = rspayload($faucet, $x, $y);
        if (!$payload) {
            echo merah."error create fingerprint!\n";
            goto reload;
        }

        $data = http_build_query([
        	  "ci_csrf_token" => "",
        	  "token" => $token,
        	  "currency" => $memek,
        	  "user_website" => "",
        	  "bh_gesture" => rand(1,10),
        	  "bh_dwell" => rand(1000,9000),
        	  "bh_interacted" => rand(1,10),
        	  "captcha" => "rscaptcha",
        	  "rscaptcha_token" => $rs_token,
        	  "rscaptcha_response" => $payload["fingerprint"],
        	  "uf" => uf(),
        	  "utt" => "Asia/Jakarta",
        	  "ls" => "id-ID,id,en-US,en"
        ]);
        $url = host."/faucet/verify";
        $claim = skibidixxx($url, "POST", $data, $c);
        if (strpos($claim, "Good job!") !== false) {
            $msg = explode("'", explode("text: '", $claim)[1])[0];
            $timer = explode(' -', explode('let wait = ', $claim)[1])[0];
            echo putih."[INFO] ".hijau.$msg."\n";
            timer($timer);

        } elseif (strpos($claim, "Invalid") !== false){
            echo "[INFO] Invalid captcha or invalid claim!\n";
            goto reload;

        } elseif (strpos($claim, "The faucet does not have sufficient funds") !== false) {
	    echo putih."------------------------------------------------------\n";
            echo kuning."[INFO] The faucet does not have sufficient funds.\n";
            echo putih."enter to menu..";
            trim(fgets(STDIN));
            goto dash;
        } else {
            echo merah."Error tidak tahu gua anjay!";
	    sleep(1.8);
	    echo "\r                                  \r";
            goto reload;
        }
    }
} else {
    echo putih."Hiii Login again ....!\n";
    @unlink($configFile);
    sleep(4);
    goto login;
}
