<template>
<div class="content clearfix">
    <header>
        <h1 class="toptitle">
            <router-link :to="{name: 'plantwatcher'}">
                Plant Irrigation Module
            </router-link>
        </h1>
    </header>
    <aside>
        <section>
            <h4>Interests...</h4>
            <ul class="list-style-none">
                <li><a href="#">Show tank</a></li>
                <li><a href="#">Water statistics</a></li>
                <li><router-link :to="{name: 'plantmanager'}">
                    Manage service
                </router-link></li>
            </ul>
        </section>
    </aside>
    <slot/>
</div>
</template>

<script>
export default {
    name: 'IrrigationLayout'
}
</script>

<style scoped>
.content > aside {
    float: left;
    margin: 0 1.0%;
    width: 15.0%;
    background-color : #D0D0D0 ;
    border: 1px solid #A8A8A8;
    border-radius: 15px;
    padding-top: 10px;
    padding-left: 10px;
    padding-bottom: 10px;
    text-align: left;
    white-space: nowrap;
}
.content > aside h4 {
    margin: 0 auto 15px 0;
}
.content > aside ul {
    margin: 0;
}
.content > section {
    float: right;
    width: 77.4%;
    margin: 0 1.0%;
    border: 1px solid lightgrey;
    border-radius: 15px;
    padding: 0 10px;
}
</style>
