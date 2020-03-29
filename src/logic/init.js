// 定义字符串格式化方法
String.prototype.format = function(){
    let str = this
    for(let arg of arguments){
        str = str.replace('%', arg)
    }
    return str
}

// 数组删除指定值
window.arrRemove = function(arr, val){
    let index = arr.indexOf(val)
    arr.splice(index, 1)
}

// 定义有元素数量上限的数组追加, 增加了cap属性的数组，不可再使用for in
window.enqueue = function(arr, elem){
    if(arr.length === arr.cap)
        arr.shift()
    arr.push(elem)
}

// 设置调试级别
const level = {log: 0, warn: 1, error: 2}
const setDebugLevel = function(level){
    if(level > 0) console.log = function(){}
    if(level > 1) console.warn = function(){}
}
setDebugLevel(level.warn)