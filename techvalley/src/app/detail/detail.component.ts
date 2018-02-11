import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Chart } from 'angular-highcharts';
import { HttpClient, HttpHeaders, HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-detail',
  templateUrl: './detail.component.html',
  styleUrls: ['./detail.component.css']
})
export class DetailComponent implements OnInit {

  private dataFrequency:string
  private id:Number;
  private startdate:string;
  private enddate:string
  private today:Date;
  private vehicalData:Array<number> = [];
  private chart:Chart = new Chart({
       chart: {
         type: 'line'
       },
       title: {
         text: 'Traffic Over Time'
       },
       credits: {
         enabled: false
       },
       series: [{
         name: 'Days Ago',
         data: []
       }],
       yAxis: {
         title: {
           text: 'Number of Cars'
         }
       }
 });

  pad(num:number, size:number): string {
      let s = num+"";
      while (s.length < size) s = "0" + s;
      return s;
  }

  constructor(private route:ActivatedRoute, private http: HttpClient) {
    this.dataFrequency = "Every Hour"
    this.today = new Date();
    this.startdate = this.today.getFullYear() + '-' + this.pad(this.today.getMonth(), 2) + '-' + this.pad(this.today.getDate(), 2);
    this.enddate = this.today.getFullYear() + '-' + this.pad(this.today.getMonth(), 2) + '-' + this.pad(this.today.getDate(), 2);
    this.getVehicalData()
  }

  getVehicalData() {
    this.http.get<Array<number> >(`http://127.0.0.1:5000/${this.id}`).subscribe(data => {
      this.vehicalData = data
      for(let vehicalDatum of this.vehicalData) {
        this.chart.addPoint(vehicalDatum);
      }
    });
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
  }
}
