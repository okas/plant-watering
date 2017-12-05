<template>
<footer>
  <hr/>
  <div>Copyright © 2017</div>
  <div>
    Powered by
    <a href="https://vuejs.org" target="_blank">
      <img src="../static/logo_vue.png">
    </a>
  </div>
</footer>
</template>

<script>
export default {
    name: 'app-footer'
}
</script>

<style>
main {
  margin-bottom: 40px;
}
</style>
<style scoped>
footer {
  font-size: 0.9em;
  text-align: center;
  position:fixed;
  bottom:0;
  clear: both;
  width: 100%;
  left: 2px;
  right: 2px;
}
footer > div {
  display: inline-block;
  margin-bottom: 10px;
  color: black;
  text-shadow: 0 0 20px hsla(0, 0%, 100%, 1),
               0 0 20px hsla(0, 0%, 100%, 1),
               0 0 20px hsla(0, 0%, 100%, 1),
               0 0 20px hsla(0, 0%, 100%, 1),
               0 0 20px hsla(0, 0%, 100%, 1),
               0 0 20px hsla(0, 0%, 100%, 1),
               0 0 20px hsla(0, 0%, 100%, 1),
               0 0 20px hsla(0, 0%, 100%, 1),
               0 0 20px hsla(0, 0%, 100%, 1),
               0 0 20px hsla(0, 0%, 100%, 1),
               0 0 20px hsla(0, 0%, 100%, 1),
               0 0 20px hsla(0, 0%, 100%, 1),
               0 0 20px hsla(0, 0%, 100%, 1),
               0 0 15px hsla(0, 0%, 100%, 1),
               0 0 15px hsla(0, 0%, 100%, 1),
               0 0 15px hsla(0, 0%, 100%, 1),
               0 0 15px hsla(0, 0%, 100%, 1),
               0 0 15px hsla(0, 0%, 100%, 1),
               0 0 15px hsla(0, 0%, 100%, 1),
               0 0 15px hsla(0, 0%, 100%, 1),
               0 0 15px hsla(0, 0%, 100%, 1),
               0 0 15px hsla(0, 0%, 100%, 1),
               0 0 15px hsla(0, 0%, 100%, 1),
               0 0 15px hsla(0, 0%, 100%, 1),
               0 0 15px hsla(0, 0%, 100%, 1),
               0 0 15px hsla(0, 0%, 100%, 1),
               0 0 5px hsla(0, 0%, 100%, 1),
               0 0 5px hsla(0, 0%, 100%, 1),
               0 0 5px hsla(0, 0%, 100%, 1),
               0 0 5px hsla(0, 0%, 100%, 1),
               0 0 5px hsla(0, 0%, 100%, 1),
               0 0 5px hsla(0, 0%, 100%, 1);
}
img {
  vertical-align: middle;
  width: 17px;
}
hr {
  height: 30px;
  border-style: solid;
  border-color: #8c8b8b;
  border-width: 1px 0 0 0;
  border-radius: 20px;
  margin-bottom: -20px;
}
hr:before {
  display: block;
  content: "";
  height: 30px;
  margin-top: -31px;
  border-style: solid;
  border-color: #8c8b8b;
  border-width: 0 0 1px 0;
  border-radius: 20px;
}
</style>
