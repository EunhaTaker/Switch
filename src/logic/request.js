const request = require('request')

let store = null
let conf = null
let self = null

const request_get = function(url, cb){
    'GET请求'
    let options = {url: url}
    console.info(url)
    request.get(options, function(err, response, body){
        // console.table(JSON.parse(body))
        if(cb) cb(JSON.parse(body))
    })
}

const pack_args = function(act, args){
    '封装参数到url, 并进行URI编码'
    let url = conf.host + conf[act] + '?'
    console.log(act, conf[act])
    let items = []
    for(let i in args){
        console.log(i, args[i])
        if(args[i] !== undefined){
            items.push(
                encodeURIComponent(conf[act + '_args'][i]) + 
                '=' + 
                encodeURIComponent(args[i])
        )}
    }
    url += items.join('&')
    return url
}

export default{
	init_store(st){
        store = st
        self = this
        conf = store.state.conf
    },

    pwd: function(cb){
        const dir = store.state.mode === 'path'? store.state.curfolder: store.state.curtagpath
        if(cb) cb(dir)
        // console.warn('环境', store.state.curfolder, store.state.curtagpath)
        return dir
    },

    reload: function(cb){
        if(store.state.mode == 'path')
            self.change_dir(store.state.curfolder, cb)
        else
            self.change_tag(store.state.curtag, cb)
    },

    list_dir : function(path, opts, cb){
        request_get(pack_args('list_path', [path, opts]), function(res){
            if(cb) cb(res)
            // res.msg值：dir, file, tag
        })
    },

    change_dir: function(path, cb){
        request_get(pack_args('change_folder', [path]), function(res){
            if(cb) cb(res)
            if(res.code == 0) store.commit('change_dir', {path:path, files:res.resource})
            else if(res.code > 100) self.reload()
        })
    },

    open_file: function(path){
        request_get(pack_args('open_file', [path]))
    },

    remove: function(paths, opts, cb){
        request_get(pack_args('remove', [paths, opts]), function(res){
            if(cb) cb(res)
            if(res.code === 0) self.reload()
        })
    },

    copy: function(srclist, dest, opts, cb){
        request_get(pack_args('copy', [srclist, dest, opts]), function(res){
            if(cb) cb(res)
            if(res.code === 0) self.reload()
        })
    },

    move: function(srclist, dest, opts, cb){
        request_get(pack_args('move', [srclist, dest, opts]), function(res){
            if(cb) cb(res)
            if(res.code === 0) self.reload()
        })
    },

    new_dir: function(path, opts, cb){
        request_get(pack_args('new_dir', [path, opts]), function(res){
            if(cb) cb(res)
            if(res.code === 0) self.reload()
        })
    },

    new_tag: function(name, color, parent, cb){
        request_get(pack_args('new_tag', [name, parent, color]), function(res){
            if(cb) cb(res)
            if(res.code <= 100) self.reload() 
        })
    },

    set_tag: function(files, add_tags, del_tags, cb){
        request_get(pack_args('set_tag', [files, add_tags, del_tags]), cb)
    },

    mod_tag: function(name, destname, color, parent, cb){
        request_get(pack_args('mod_tag', [name, destname, color, parent]), function(res){
            if(cb) cb(res)
            if(res.code <= 100) self.reload() 
        })
    },

    rm_tag: function(tags, opts, cb){
        request_get(pack_args('rm_tag', [tags, opts]), function(res){
            if(cb) cb(res)
            if(res.code <= 100) self.reload()
        })
    },
    
    change_tag: function(tag, cb){
        request_get(pack_args('change_tag', [tag]), function(res){
            if(res.code <= 100 ) store.commit('open_tag', {tag:tag, contents:res.resource, chain:res.chain})
            if(cb) cb(res)
        })
    },

    unfold: function(tags, cb){
        request_get(pack_args('unfold', [tags]), function(res){
            if(res.code<=100) store.commit('unfold_tag', res.resource)
            if(cb) cb(res)
        })
    },

    alias: function(a, c, opts, cb){
        request_get(pack_args('alias', [a, c, opts]), function(res){if(cb)cb(res)})
    },

    help: function(cmd, cb){
        request_get(pack_args('help', [cmd]), res=>{if(cb)(cb(res))})
    },

    tab_cmd: function(target, type, cb){
        request_get(pack_args('tab_cmd', [target, type]), res=>{if(cb)cb(res.res, res.perfix)})
    },

    get_detail: function(target, type, cb){
        request_get(pack_args('get_detail', [target, type]), cb)
    }
}