class TreeVisitor{
    public static void main(String[] a){
        System.out.println(new TV2().f());  // HERE privateMethod
    }
}

class TV {

    private int f(){
        return 0;
    }

}

class TV2 extends TV {
    public int Start() {
        return 0;
    }
}
