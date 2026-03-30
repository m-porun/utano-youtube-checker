/**
 * 六甲おろしカウンター GAS API
 * 動画別で六甲おろしを歌った数をJSONで返す
 */

var SHEET_NAME = "rokko_count";
var CACHE_TTL = 21600; // 6時間（秒）

function doGet() {
  var cache = CacheService.getScriptCache();
  var cached = cache.get("rokko_json");

  if (cached) {
    return ContentService.createTextOutput(cached).setMimeType(
      ContentService.MimeType.JSON,
    );
  }

  var json = buildJson();
  cache.put("rokko_json", json, CACHE_TTL);

  return ContentService.createTextOutput(json).setMimeType(
    ContentService.MimeType.JSON,
  );
}

function buildJson() {
  var sheet =
    SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  var rows = sheet.getDataRange().getValues();
  // ヘッダー: [検索件数, 動画タイトル, 動画URL, セットリスト, 六甲おろしが歌われた数, 六甲おろし番号, タイムスタンプ]
  var data = rows.slice(1);

  // 動画URLをキーに集約
  var videoMap = {};

  for (var i = 0; i < data.length; i++) {
    var row = data[i];
    var index = row[0];
    var title = row[1];
    var url = row[2];
    var rokkoCount = Number(row[4]);
    var timestamp = row[6];

    if (rokkoCount === 0 || !url) continue;

    // videoId を URL から抽出
    var match = String(url).match(/[?&]v=([^&]+)/);
    if (!match) continue;
    var videoId = match[1];

    if (!videoMap[videoId]) {
      videoMap[videoId] = {
        index: index,
        title: title,
        videoId: videoId,
        rokkoCount: rokkoCount,
        timestamps: [],
      };
    }

    var rokkoNo = Number(row[5]);
    if (timestamp) {
      videoMap[videoId].timestamps.push({ rokkoNo: rokkoNo, value: String(timestamp) });
    }
  }

  var videos = [];
  var totalCount = 0;
  var keys = Object.keys(videoMap);
  for (var j = 0; j < keys.length; j++) {
    var v = videoMap[keys[j]];
    // rokkoNo 順にソートしてタイムスタンプ文字列の配列に変換
    v.timestamps.sort(function(a, b) { return a.rokkoNo - b.rokkoNo; });
    v.timestamps = v.timestamps.map(function(t) { return t.value; });
    totalCount += v.rokkoCount;
    videos.push(v);
  }

  return JSON.stringify({
    totalCount: totalCount,
    updatedAt: Utilities.formatDate(
      new Date(),
      "Asia/Tokyo",
      "yyyy-MM-dd",
    ),
    videos: videos,
  });
}

/**
 * キャッシュを手動クリアする関数。
 * スプレッドシート更新後にスクリプトエディタから実行する。
 */
function clearCache() {
  CacheService.getScriptCache().remove("rokko_json");
}
