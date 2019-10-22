class Factorial {
    public static void Main( String[] a ) {
        System.out.println( new FactImpl().Calc( 10 ) );
    }
}

// comment

/* another one cooment */

class FactImpl {
    public int Calc( int num ) {
        int accum;
        if( num < 1 ) {
            accum = 1;
        } else {
            accum = num * (this.Calc( num - 1 ) );
        }
        return  accum;
    }
}
