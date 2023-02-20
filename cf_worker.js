export default {
  async fetch(request, env) {
    return await handleRequest(request).catch(
      (err) => new Response(err.stack, { status: 500 })
    )
  }
}

async function handleRequest(request) {
  const { pathname } = new URL(request.url);

  if (pathname.startsWith("/api")) {
    return new Response(JSON.stringify({ pathname }), {
      headers: { "Content-Type": "application/json" },
    });
  }

  if (pathname.startsWith("/status")) {
    const httpStatusCode = Number(pathname.split("/")[2]);

    return Number.isInteger(httpStatusCode)
      ? fetch("https://http.cat/" + httpStatusCode)
      : new Response("That's not a valid HTTP status code.");
  }

  let getTodayStr = (timeZone) => {
    let date = new Date();

    let utcDate = new Date(date.toLocaleString('en-US', { timeZone: "UTC" }));
    let tzDate = new Date(date.toLocaleString('en-US', { timeZone: timeZone }));
    let offset = tzDate.getTime() - utcDate.getTime();
    console.log(offset);

    date.setTime( date.getTime() + offset );

    return date.toJSON();
  };

  console.log(pathname.split("/"))
  let todayStr = getTodayStr("Asia/Shanghai").substr(0, 10);
  const splits = pathname.split("/");
  if (splits.length == 3) {
    let cat = splits[1];
    let subCat = splits[2];
    let target_file = 'https://assets.aidenli.net/arxiv-daily/' + todayStr +  '_' + cat.toLowerCase() + '_' + subCat.toUpperCase() + '.zip';
    console.log("Redirecting to" + target_file)
    return Response.redirect(target_file, 301);
  }

  return Response.redirect("https://blog.aidenli.net", 301);
}