<%* 
let file = tp.file.find_tfile(tp.date.now("YYYY-MM-DD")) 
console.log("000000");
if (!file) {
	console.log("11111");
	let templateFile = tp.file.find_tfile("DailyNote"); // 模板文件名
	if (!templateFile) {
        new Notification("模板文件 'DailyNote' 未找到！");
        return;
    }
    let folderPath = app.vault.getAbstractFileByPath("DailyNotes");
    file = await tp.file.create_new(
        templateFile, // 模板
        tp.date.now("YYYY-MM-DD"), // 新文件名
        false,
        folderPath
    );
}
if (file) {
	console.log("2222");
	const loggedItem = await tp.system.prompt("What's Up?") 
	const time = tp.date.now("HH:mm") 
	const content = (await app.vault.read(file)).split("\n") 
	const index = content.indexOf("## What happened today?") 
	// 如果未找到标题，提示用户
    if (index === -1) {
        new Notification("标题 '## What happened today?' 未找到！");
        return;
    }
	content.splice(index + 1, 0, `- ${time} - ${loggedItem}`) 
	await app.vault.modify(file, content.join("\n")) 
} else { 
	new Notification("No Daily Note Found!") 
} 
%>