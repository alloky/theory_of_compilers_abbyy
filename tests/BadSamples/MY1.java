class TreeVisitor{
    public static void main(String[] a){
        System.out.println(new TV().Start());  // HERE privateMethod
    }
}

class TV {

    private int Start(){
        return 0 ;
    }

}
