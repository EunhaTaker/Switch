<template>
<div >
    <div v-for='item of tags' style="width: 100%">
        <div class='tree-item' v-if='(typeof item) !== "object"'>
            {{item}} 
            <input :id='item' class='item-check' type="checkbox" @change="onChange($event, tags)"/>
            <label :for='item'></label>
        </div>
        <!-- <div v-else> -->
            <menutree v-else class='tree' :tags='item' collapse='false'/>
        <!-- </div> -->
    </div>
</div>
</template>

<script>
import menutree from './menutree4tags.vue'
let checks = []
let checkNodes = []
export default{
    name: 'menutree',
    components: {
        menutree
    },
    props:['tags'],
    methods: {
        onChange: function(event, tag){
            const target = event.target
            // console.warn(target.checked)
            if(target.checked){
                checks.push(tag)
                checkNodes.push(target)
            }else{
                window.arrRemove(checks, tag)
                window.arrRemove(checkNodes, target)
            }
            console.warn(checks)
        }
    }
}
</script>

<style>
.tree-item {
    padding: 3px;
    width: 100%;
    /* height: 30px; */
    border: 1px solid;
    border-radius: 5px;
    text-align: left;
    font-size: 20px;
    /* background-color: aquamarine; */
    vertical-align: middle;

    /* content: ''; */

}
.tree-item label{
	width: 20px;
	height: 20px;
	position: absolute;
	top: 4px;
	left: 4px;
	/* cursor: pointer;
	background: -moz-linear-gradient(top, #222222 0%, #45484d 100%);
	background: -webkit-linear-gradient(top, #222222 0%, #45484d 100%);
	background: linear-gradient(to bottom, #222222 0%, #45484d 100%);
	-moz-border-radius: 50px;
	-webkit-border-radius: 50px;
	border-radius: 50px; */
	/* -moz-box-shadow: inset 0px 1px 1px rgba(0, 0, 0, 0.5), 0px 1px 0px white;
	-webkit-box-shadow: inset 0px 1px 1px rgba(0, 0, 0, 0.5), 0px 1px 0px white;
	box-shadow: inset 0px 1px 1px rgba(0, 0, 0, 0.5), 0px 1px 0px white; */

    /* position: absolute;
    border-right: 1px solid #fff;
    border-bottom: 1px solid #fff;
    background: #fff;
    transform: rotate(45deg);
    -webkit-transform: rotate(45deg);
    -moz-transform: rotate(45deg);
    -ms-transform: rotate(45deg);
    transition: all 0.3s ease;
    -webkit-transition: all 0.3s ease;
    -moz-transition: all 0.3s ease; */
}
/* .tree-item label::after {
	content: '';
	width: 9px;
	height: 5px;
	position: absolute;
	top: 5px;
	left: 4px;
	border: 3px solid #fcfff4;
	border-top: none;
	border-right: none;
	background: transparent;
	filter: progid:DXImageTransform.Microsoft.Alpha(Opacity=0);
	opacity: 0;
	-moz-transform: rotate(-45deg);
	-ms-transform: rotate(-45deg);
	-webkit-transform: rotate(-45deg);
	transform: rotate(-45deg);
} */
.tree-item *{
    vertical-align: middle;
    /* align-content: center;
    align-self: center; */
}
.tree {
    width: 96%;
    float: right;
}
.item-check{
    /* margin-bottom: 3px; */
    float: right;
    height: 20px;
    /* bottom: 0; */
    /* vertical-align: bottom; */
}
</style>
