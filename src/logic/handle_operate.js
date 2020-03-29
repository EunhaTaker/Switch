import req from './request.js'
import Swal from 'sweetalert2'

export default {
    refresh: function(cb){
        req.reload(function(res){
            if(cb) cb(res)
        })
    },
    mkdir: function(dir, cb){
        req.new_dir(req.pwd() + dir, undefined, cb)
    },
    cd: function(dir, cb){
        req.change_dir(dir, cb)
    },
    rm: function(targets, type, cb){
        if(type == 'path'){
            req.remove(targets, ['-r'], cb)
        }else{
            req.rm_tag(targets, ['-r'], cb)
        }
    },
    cp: function(srcFullName, cb){
        req.copy(srcFullName, req.pwd(), ['-r'], cb)
    },
    mv: function(srcFullName, destName, bRename, cb){
        req.move(srcFullName, bRename? req.pwd()+destName: req.pwd(), ['-r'], cb)
    },
    opentag: function(tagname, cb){
        req.change_tag(tagname, cb)
    },
    modtag: function(name, destname, color, parent, cb){
        req.mod_tag(name, destname, color, parent, cb)
    },
    newtag: function(name, color, parent, cb){
        req.new_tag(name, color, parent, cb)
    },
    openImg: function(fullname, conf){
        Swal.fire({
            imageUrl: conf.host + conf.read_file+"?"+conf.read_file_args[0]+"="+ fullname,
            showConfirmButton: false,
        })
    },
    open: function(fullname){
        req.open_file(fullname)
    },
    detail: function(target, type, cb){
        req.get_detail(target, type, cb)
    }
}