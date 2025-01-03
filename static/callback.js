document.addEventListener("DOMContentLoaded", function () {
  const url = window.location.href;
  const hasHash = url.includes("/auth/callback#");
  const hasQuery = url.includes("/auth/callback?");

  if (hasHash && !hasQuery) {
    // '#'이 있고 '?'가 없을 때만 변환
    const newUrl = url.replace(/\/auth\/callback#/, "/auth/callback?");
    window.location.replace(newUrl);
  }
});
